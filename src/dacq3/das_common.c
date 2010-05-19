/* title:   das_common.c

** author:  jamie mazer
** created: Mon Mar  4 16:41:26 2002 mazer 
** info:    dasXX_server.c common functions
** history:
**
** Thu Apr  4 14:06:25 2002 mazer 
**   - changed calls to setpriority to also bump scheduler priority up to
**	realtime (SCHED_RR)
**
** Fri Aug 23 16:53:54 2002 mazer 
**   - Modified timestamp() to use the RDTSC for speed.  At
**     1 gHz, the 8byte (64bit) counter would overflow in:
**       (2^64) / (1e9) secs = 1.8e10s, or more than 500 years..
**     so, I'm assuming overflow is NOT a problem right now..
**
** Thu Dec 19 14:03:32 2002 mazer 
**   added EYELINK_TEST mode
**
** Wed Apr 16 10:41:16 2003 mazer 
**   added parsing of $XXEYELINK_OPTS to allow setting of eyelink
**   parameters in the pyperc config file...
**
** Sun Nov  6 10:06:36 2005 mazer 
**   added $EYELINK_FILE to save native EDF file during run.
**
** Tue Jan 17 11:37:56 2006 mazer 
**   - added $(CWD)/eyelink.ini file --> supplemental commands for the
**     eyelink
**   - made sure stderr messages all contain progname..
**
** Mon Jan 23 10:01:22 2006 mazer 
**   Added handling of FIXWIN.vbias for vertical elongation of the
**   fixation window.
**
** Fri Mar 10 10:08:25 2006 mazer 
**   Added stub support of a usb joystick or keypad. Right now the
**   device is detected and initialized, but nothing's done yet
**   with the signals.
**
** Thu Apr 13 09:38:38 2006 mazer 
**   merged stand-alone iscan_server code into the main event
**   loop for das_common, so all XXX_server's will be able to
**   talk to the iscan without competition from a separate
**   process.
**
** Thu May 25 11:40:58 2006 mazer 
**   changed z from int to float in mainloop() to avoid overflow
**   errors on (x*x)+(y*y) with ISCAN...
**
** Tue Nov 28 16:58:07 2006 mazer 
**   added support for a ms-resolution alarm that sends interupts
**   the client/parent process
**
** Tue Apr  3 10:39:56 2007 mazer 
**   added support for "-notracker" mode (for acutes)
**
** Fri Jun 15 15:09:05 2007 mazer 
**   added arange (analog input range) for comedi drivers
**
** Thu Dec 18 11:39:36 2008 mazer 
**   - moved eyelink and iscan specific code into separate files
**     that get included here:
**       - iscan.c
**       - eyelink.c
**   - reorganized the mainloop to sample each channel only once
**     and then usleep for a bit to reduce CPU load. original
**     behavior can be restored by #defining SPIN_SAMPLE (which
**     averages over the 1ms interval in a tight loop).
**
** Tue May  5 14:40:33 2009 mazer 
**   - removed EYELINK_TEST mode completely..
**   - changed private XXxxx env vars to XX_xxxx
*/

#include <unistd.h>
#include <sys/time.h>
#include <sys/errno.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <signal.h>
#include <sched.h>
#include <math.h>

#include "psems.h"
#ifdef CHANGE_NAME
# include "procname.h"
#endif
#include "usbjs.h"

//#define SPIN_SAMPLE 1

static char *_tmodes[] = {
  "ANALOG", "ISCAN", "EYELINK", "EYEJOY", "NONE"
};
#define ANALOG		0
#define ISCAN		1
#define EYELINK		2
#define EYEJOY		3
#define NONE		4

#define INSIDE		1
#define OUTSIDE		0

static int tracker_mode = ANALOG;
static int semid = -1;
static unsigned long long ticks_per_ms = 0;
static int swap_xy = 0;
static int usbjs_dev = -1;
static int iscan_x, iscan_y, iscan_p;
static double arange = 10.0;

#include "iscan.c"
#include "eyelink.c"

static double find_clockfreq()	/* get clock frequency in Hz */
{
  FILE *fp;
  char buf[100];
  double mhz;

  if ((fp = fopen("/proc/cpuinfo", "r")) == NULL) {
    fprintf(stderr, "%s: can't open /proc/cpuinfo\n", progname);
    exit(1);
  }
  mhz = -1.0;
  while (fgets(buf, sizeof(buf), fp) != NULL) {
    if (sscanf(buf, "cpu MHz         : %lf", &mhz) == 1) {
      break;
    }
  }
  return(mhz * 1.0e6);
}

#if defined(__i386__)

// this macro doesn't quite work

#define RDTSC(x) __asm__ __volatile__ ( ".byte 0x0f,0x31"		\
					:"=a" (((unsigned long*)&x)[0]), \
					 "=d" (((unsigned long*)&x)[1]))

static unsigned long timestamp(int init)
{
  static unsigned long long timezero;
  unsigned long long now;

  RDTSC(now);			/* get cycle counter from hardware TSC */
  if (init) {
    timezero = now;
    return(0);
  } else {
    /* use precalibrated ticks_per_ms to convert to real time.. */
    return((unsigned long)((now - timezero) / ticks_per_ms));
  }
}

#elif defined(__x86_64__)

/* need to use different method to access real time clock
** under 64bit kernel!
*/

static unsigned long timestamp(int init)
{
  static unsigned long long timezero;
  unsigned long long now;
  unsigned a, d;

  asm("cpuid");
  asm volatile("rdtsc" : "=a" (a), "=d" (d));
  now = ((unsigned long long)a) | (((unsigned long long)d) << 32);

  if (init) {
    timezero = now;
    return(0);
  } else {
    /* use precalibrated ticks_per_ms to convert to real time.. */
    return((unsigned long)((now - timezero) / ticks_per_ms));
  }
}
#else
#error "real time clock not defined this arch"
#endif

static void perror2(char *s, char *file, int line)
{
  char *p = (char *)malloc(strlen(progname)+strlen(s)+25);

  sprintf(p, "%s (file=%s, line=%d):%s", progname, file, line, s);
  perror(p);
  free(p);
}

static void resched(int rt)
{
#ifdef ALLOW_RESCHED
  struct sched_param p;

  /* change scheduler priority from OTHER to RealTime/RR or vice versa */

  if (sched_getparam(0, &p) >= 0) {
    if (rt) {
      p.sched_priority = SCHED_RR;
      sched_setscheduler(0, SCHED_RR, &p);
    } else {
      p.sched_priority = SCHED_OTHER;
      sched_setscheduler(0, SCHED_OTHER, &p);
    }
  }
#endif
}

static void mainloop(void)
{
  register int i, ii, lastpri, setpri;
  register float x, y, z, pa, tmp, calx, caly;
  float tx, ty, tp;
  unsigned long last_ts = 0, ts;
  unsigned int eyelink_t;
  int eyelink_new;
  int k;
  int jsbut, jsnum, jsval;
  unsigned long jstime;

  register float sx=0, sy=0;
  int si, sn, last;
  float sbx[MAXSMOOTH], sby[MAXSMOOTH];

  /*
   * calx/caly are the gain+offset adjusted eye position values
   * x/y are the raw values
   */
  calx = caly = x = y = pa = -1;
  y = x = 0.0;
  for (si = 0; si < MAXSMOOTH; si++) {
    sbx[si] = sby[si] = 0.0;
  }
  si = 0;

  errno = 0;
  LOCK(semid);
  k = dacq_data->dacq_pri;
  UNLOCK(semid);

  if (setpriority(PRIO_PROCESS, 0, k) == 0 && errno == 0) {
    fprintf(stderr, "%s: bumped priority %d\n", progname, k);
    lastpri = k;
    if (lastpri < 0) {
      resched(1);
    }
    setpri = 1;
  } else {
    fprintf(stderr, "%s: failed to change priority\n", progname);
    setpri = 0;
    lastpri = 0;
  }

  timestamp(1);			/* initialize the timestamp to 0 */

  fprintf(stderr, "%s: tracker_mode=%s (%d)\n", progname,
	  _tmodes[tracker_mode], tracker_mode);

  /* signal client we're ready */
  LOCK(semid);
  dacq_data->das_ready = 1;
  fprintf(stderr, "%s: ready\n", progname);
  UNLOCK(semid);

  do {
    /* sample converters as fast as possible and accumulate
     * into temp buffer for averaging at the end of the sample
     * period (1ms).  This replaces spin-locking code.
     */
#ifdef SPIN_SAMPLE
    {
      int naccum = 0;
      long accum[NADC];

      do {
	/* sample the converters & acculumate values */
	for (i = 0; i < NADC; i++) {
	  if (naccum == 0) {
	    accum[i] = ad_in(i);
	  } else {
	    accum[i] += ad_in(i);
	  }
	}
	naccum += 1;
	if (tracker_mode == ISCAN) {
	  iscan_read();
	}
      } while (((ts = timestamp(0)) - last_ts) < 1);
      last_ts = ts;
      
      /* adjust for # of acculumated values */
      for (i = 0; i < NADC; i++) {
	LOCK(semid);
	dacq_data->adc[i] = (int)(accum[i] / naccum);
	UNLOCK(semid);
      }
    }
#else
    // usleep(500); --> looks like usleep actually sleeps for more
    // like 8ms minimum... so we're back to spinning..

    /* and then wait for the 1ms interval to elapse */
    while ((timestamp(0) - last_ts) < 1) {
      ;
    }
    /* now quickly sample all the converters just once */
    for (i = 0; i < NADC; i++) {
      dacq_data->adc[i] = ad_in(i);
    }
    if (tracker_mode == ISCAN) {
      iscan_read();
    }
    ts = last_ts = timestamp(0);
#endif

    if (usbjs_dev > 0) {
      if (usbjs_query(usbjs_dev, &jsbut, &jsnum, &jsval, &jstime)) {
	if (jsbut) {
	  /* button press: jsnum is button number, jsval is up/down */
	  if (jsnum < NJOYBUT) {
	    LOCK(semid);
	    dacq_data->js[jsnum] = jsval;
	    UNLOCK(semid);
	  }
	} else if (jsbut == 0 && jsnum == 0) {
	  /* x-axis motion, jsval indicates the current value */
	  dacq_data->js_x = jsval;
	} else if (jsbut == 0 && jsnum == 1) {
	  /* y-axis motion, jsval indicates the current value */
	  dacq_data->js_y = jsval;
	}
      }
    }

    switch (tracker_mode)
      {
      case NONE:
	x = y = pa = 0;
	break;
      case ISCAN:
	x = iscan_x;
	y = iscan_y;
	pa = iscan_p;
	break;
      case EYELINK:
	if (eyelink_read(&tx, &ty, &tp, &eyelink_t, &eyelink_new) != 0) {
	  x = tx;
	  y = ty;
	  pa = tp;
	}
	break;
      case EYEJOY:
	LOCK(semid);
	x = x + (dacq_data->js_x > 0 ? 1 : dacq_data->js_x < 0 ? -1 : 0)/100.0;
	y = y - (dacq_data->js_y > 0 ? 1 : dacq_data->js_y < 0 ? -1 : 0)/100.0;
	dacq_data->adc[0] = x;
	dacq_data->adc[1] = y;
	UNLOCK(semid);
	pa = -1;
	break;
      default:
	x = dacq_data->adc[0];
	y = dacq_data->adc[1];
	pa = -1;
	break;
      }

    if (swap_xy) {
      tmp = x; x = y; y = tmp;
    }

    /* smooth (if necessary) raw eye position trace */
    LOCK(semid);
    sn = dacq_data->eye_smooth;
    if (sn > MAXSMOOTH) {
      sn = MAXSMOOTH;
    }
    UNLOCK(semid);

    if (sn > 1) {
      /* remove old point, add new point to smoothing sum */
      sx = sx - sbx[si] + x;
      sy = sy - sby[si] + y;

      /* add new (unsmoothed data points) to smoothing buffer */
      sbx[si] = x;
      sby[si] = y;
      si = (si + 1) % sn;

      /* calc smoothed point */
      x = sx / sn;
      y = sy / sn;
    }

    /* convert from raw to pixel domain and save in eye_x/eye_y */
    LOCK(semid);
    calx = (dacq_data->eye_xgain * x) - dacq_data->eye_xoff;
    caly = (dacq_data->eye_ygain * y) - dacq_data->eye_yoff;
    dacq_data->eye_x = (int)((calx > 0) ? (calx+0.5) : (calx-0.5));
    dacq_data->eye_y = (int)((caly > 0) ? (caly+0.5) : (caly-0.5));
    dacq_data->eye_pa = pa;
    UNLOCK(semid);
    
    /* read digital input lines */
    if (usbjs_dev >= 0) {
      /* if joystick device is available (even if it's not
       * being used as an eye tracker, use buttons as digital inputs..
       */
      for (i = 0; i < 4; i++) {
	LOCK(semid);
	last = dacq_data->din[i];
	dacq_data->din[i] = dacq_data->js[i];
	if (dacq_data->din[i] != last) {
	  dacq_data->din_changes[i] += 1;
	  if (dacq_data->din_intmask[i]) {
	    dacq_data->int_class = INT_DIN;
	    dacq_data->int_arg = i;
	    kill(getppid(), SIGUSR1);
	  }
	}
	UNLOCK(semid);
      }
    } else {
      /* otherwise, fall back to comedi DIO lines etc */
      dig_in();
    }

    /* set digital output lines, only if the strobe's been set */
    LOCK(semid);
    k = dacq_data->dout_strobe;
    UNLOCK(semid);
    if (k) {
      dig_out();
      /* reset the strobe (as if it were a latch */
      LOCK(semid);
      dacq_data->dout_strobe = 0;
      UNLOCK(semid);
    }

    LOCK(semid);
    dacq_data->timestamp = ts;
    k = dacq_data->adbuf_on;

    /* check alarm status */
    if (dacq_data->alarm_time && ts < dacq_data->alarm_time) {
      /* alarm set and expired -- clean and send interupt to
       * client (ie, parent)
       */
      dacq_data->alarm_time = 0;
      dacq_data->int_class = INT_ALARM;
      dacq_data->int_arg = 0;
      kill(getppid(), SIGUSR1);
    }
    UNLOCK(semid);


    /* Stash the data, if recording is on:
     *  adbuf_t,x,y <- calibrated eye signal
     *  adbuf_pa <- pupil area, if available (eyelink only)
     *  adbuf_c[01234] <- raw data streams; in eyelink test mode
     *    these are:
     *     c0 <- eyelink x
     *     c1 <- eyelink y
     *     c2 <- coil raw x
     *     c3 <- coil raw y
     *     c4 <- eyelink pupil area
     */
    if (k) {
      LOCK(semid);
      k = dacq_data->adbuf_ptr;
      dacq_data->adbuf_t[k] = ts;
      dacq_data->adbuf_x[k] = dacq_data->eye_x;
      dacq_data->adbuf_y[k] = dacq_data->eye_y;
      dacq_data->adbuf_pa[k] = dacq_data->eye_pa;

      /* the raw analog values are stuffed in, which
       * are usually raw x,y values off the coil, unless you're
       * using them for something else (and have iscan/eyelink)
       */
      for (ii=0; ii < NADC; ii++) {
	dacq_data->adbufs[ii][k] = dacq_data->adc[ii];
      }
      /* Mon Jan 16 09:25:34 2006 mazer 
       *  set up saving EDF-time to c4 channel for debugging
       dacq_data->adbuf_c4[k] = eyelink_t;
      */
      if (++dacq_data->adbuf_ptr > ADBUFLEN) {
	dacq_data->adbuf_overflow++;
	dacq_data->adbuf_ptr = 0;
      }
      UNLOCK(semid);
    }

    /* check fixwins for in/out events */
    for (i = 0; i < NFIXWIN; i++) {
      LOCK(semid);
      k = dacq_data->fixwin[i].active;
      UNLOCK(semid);
      if (k) {
	LOCK(semid);
	x = dacq_data->eye_x - dacq_data->fixwin[i].cx;
	y = (dacq_data->eye_y - dacq_data->fixwin[i].cy) /
	  dacq_data->fixwin[i].vbias;
	UNLOCK(semid);
	
	z = (x * x) + (y * y);
	
	LOCK(semid);
	if (z < dacq_data->fixwin[i].rad2) {
	  /*
	   * eye is now INSIDE the fixation window -- stop counting
	   * transient breaks
	   */
	  dacq_data->fixwin[i].state = INSIDE;
	  dacq_data->fixwin[i].fcount = 0;
	} else {
	  /*
	   * eye is outside the fixation window, but could be shot noise..
	   */
	  if (dacq_data->fixwin[i].state == INSIDE) {
	    /*
	     * eye was inside last sample, so the break just happened
	     * reset the break counter and start counting # samples
	     * outside fixation window
	     */
	    dacq_data->fixwin[i].fcount = 1;
	    dacq_data->fixwin[i].nout = 0;
	  }
	  dacq_data->fixwin[i].state = OUTSIDE;
	  if (dacq_data->fixwin[i].fcount) {
	    dacq_data->fixwin[i].nout += 1;
	    if (dacq_data->fixwin[i].nout > dacq_data->fixbreak_tau) {
	      /* number of samples the eye's been out of the window
	       * has exceeded the limit defined by fixbreak_tau, count
	       * this as a real fixation break.
	       */
	      if (dacq_data->fixwin[i].broke == 0) {
		/* stash time if it's the first break */
		dacq_data->fixwin[i].break_time =  dacq_data->timestamp;
	      }
	      dacq_data->fixwin[i].broke = 1;
	      if (dacq_data->fixwin[i].genint) {
		/* send interupt to parent */
		dacq_data->int_class = INT_FIXWIN;
		dacq_data->int_arg = 0;
		dacq_data->fixwin[i].genint = 0;
		kill(getppid(), SIGUSR1);
		/* fprintf(stderr,"das: sent int, disabled\n"); */
	      }
	    }
	  }
	}
	UNLOCK(semid);
      }
    }

    /* possibly bump up or down priority on the fly */
    LOCK(semid);
    k = dacq_data->dacq_pri;
    UNLOCK(semid);
    if (setpri && lastpri != k) {
      lastpri = k;
      errno = 0;
      if (setpriority(PRIO_PROCESS, 0, k) == -1 && errno) {
	/* disable future priority changes */
	setpri = 0;
      }
      if (lastpri < 0) {
	resched(1);
      }
    }
    LOCK(semid);
    k = dacq_data->terminate;
    UNLOCK(semid);
  } while (! k);

  fprintf(stderr, "%s: terminate signaled\n", progname);
  iscan_halt();
  eyelink_halt();
  if (usbjs_dev >= 0) {
    usbjs_close(usbjs_dev);
  }

  /* no longer ready */
  LOCK(semid);
  dacq_data->das_ready = 0;
  UNLOCK(semid);

  // this isn't needed, halt() gets called automatically via atexit()
  //halt();
}

int main(int ac, char **av, char **envp)
{
  char *p;
  float mhz;

#ifdef CHANGE_NAME
  init_set_proc_title(ac, av, envp);
#endif

  p = rindex(av[0], '/');
  progname = p ? (p + 1) : av[0];

  ticks_per_ms = (unsigned long long)(0.5 +
				      ((mhz = find_clockfreq()) / 1000.0));

  if ((semid = psem_init(SEMKEY)) < 0) {
    perror("psem_init");
    fprintf(stderr, "%s: can't init semaphore\n", progname);
    exit(1);
  }

  // get requested analog input range for comedi device (+- ARANGE volts)
  if ((p = getenv("XX_ARANGE")) != NULL) {
    double d;
    if (sscanf(p, "%lf", &d) == 1) {
      arange = d;
    }
  }

  init();
  fprintf(stderr, "%s: initted\n", progname);

  if (av[1] && (strcmp(av[1], "-iscan") == 0)) {
    iscan_init(av[2]);
  } else if (av[1] && (strcmp(av[1], "-eyelink") == 0)) {
    eyelink_init(av[2]);
  } else if (av[1] && (strcmp(av[1], "-eyejoy") == 0)) {
    tracker_mode = EYEJOY;
  } else if (av[1] && (strcmp(av[1], "-notracker") == 0)) {
    tracker_mode = NONE;
    fprintf(stderr, "%s: no tracker mode\n", progname);
  }

  if (getenv("XX_SWAP_XY")) {
    /* this option is useful ONLY if the camera is rotated, like with
     * the original software release for the eyelink ELCL...
     */
    swap_xy = 1;
    fprintf(stderr, "%s: swapping X and Y\n", progname);
  }

  if ((p = getenv("XX_USBJS")) != NULL) {
    usbjs_dev = usbjs_init(p);
    if (usbjs_dev < 0) {
      fprintf(stderr, "%s: can't open joystick %s\n", progname, p);
    } else {
      fprintf(stderr, "%s: joystick at %s configured\n", progname, p);
      LOCK(semid);
      dacq_data->js_enabled = 1;
      UNLOCK(semid);
    }
  }

  mainloop();
  fprintf(stderr, "%s: bye bye\n", progname);
  exit(0);
}

