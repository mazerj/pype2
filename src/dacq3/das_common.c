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
*/

#include <unistd.h>
#include <sys/time.h>
#include <sys/errno.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <signal.h>
#include <sched.h>

#include "psems.h"
#ifdef CHANGE_NAME
# include "procname.h"
#endif
#include "usbjs.h"

/* these are eyelink API header files */
#include "eyelink.h"
#include "eyetypes.h"

/* this has set_eyelink_address() etc.. */
#include "exptsppt.h"

/* ez-serial library for iscan interface */
#include "libezV24-0.0.3/ezV24.h"

static char *_tmodes[] = { "ANALOG", "ISCAN", "EYELINK", "EYELINK_TEST" };
#define ANALOG		0
#define ISCAN		1
#define EYELINK		2
#define EYELINK_TEST	3

#define INSIDE		1
#define OUTSIDE		0

static int tracker_mode = ANALOG;
static int semid = -1;
static unsigned long long ticks_per_ms = 0;
static int eyelink_camera = -1;
static int swap_xy = 0;
static int usbjs_dev = -1;
static v24_port_t *iscan_port = NULL;
static int iscan_x, iscan_y, iscan_p;

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

static void iscan_init(char *server, char *dev)
{
  if ((iscan_port = v24OpenPort(dev, V24_NO_DELAY | V24_NON_BLOCK)) == NULL) {
    fprintf(stderr, "%s: iscan_init can't open \"%s\"\n.", progname, dev);
    exit(1);
  }
  v24SetParameters(iscan_port, V24_B115200, V24_8BIT, V24_NONE);

  tracker_mode = ISCAN;
  fprintf(stderr, "%s: opened iscan_port\n", progname);
}

static void iscan_halt()
{
  if (iscan_port) {
    v24ClosePort(iscan_port);
    fprintf(stderr, "%s: closed iscan_port\n", progname);
  }
}

static void iscan_read()
{
  static unsigned char buf[25];
  static int bp = -1;
  static short *ibuf;
  static int lastc = -1;
  int c;

  /* initialize the read buffer */
  if (bp < 0) {
    for (bp = 0; bp < sizeof(buf); bp++) {
      buf[bp] = 0;
    }
    bp = -1;
    ibuf = (short *)buf;
    iscan_x = 99999;
    iscan_y = 99999;
    iscan_p = 0;
  }

  if ((c = v24Getc(iscan_port)) < 0) {
    return;
  }
  if (c == 'D') {
    if (lastc == 'D') {
      lastc = -1;
      bp = 0;
    } else {
      lastc = c;
    }
    return;
  }
  if (bp >= 0) {
    buf[bp] = 0x00ff & c;
    if (bp == 7) {
      if (ibuf[0] || ibuf[1] || ibuf[2] || ibuf[3]) {
	iscan_x = (float) (ibuf[0] - ibuf[2] + 4096);
	iscan_y = (float) (ibuf[1] - ibuf[3] + 4096);
	iscan_p = (float) (1000.0);
	return;
      } else {
	iscan_x = (float) 99999;
	iscan_y = (float) 99999;
	iscan_p = (float) 0;
	return;
      }
    } else {
      if (++bp > 7) {
	fprintf(stderr, "something bad happened.\n");
      }
    }
  }
}


static void eyelink_init(char *ip_address)
{
  char *p, *q, *opts, buf[100];
  extern char *__progname;
  char *saved;
  FILE *fp;
  

  fprintf(stderr, "%s/eyelink_init: trying %s\n", progname, ip_address);

  saved = malloc(strlen(__progname) + 1);
  strcpy(saved, __progname);
#ifdef CHANGE_NAME
  set_proc_title("eyelink_thread");
#endif

  //begin_realtime_mode();
  set_eyelink_address(ip_address);
  
  if (open_eyelink_connection(0)) {
    fprintf(stderr, "\n%s/eyelink_init: can't open connection to tracker\n",
	    progname);
    return;
  }
  set_offline_mode();

  /* 16-apr-2003: step through the XXEYELINK_OPTS env var (commands
   * separated by :'s) and set each command to the eyelink, while
   * echoing to the console..  This variable is setup by pype before
   * dacq_start() gets called..
   */
  opts = getenv("XXEYELINK_OPTS");
  for (q = p = opts; *p; p++) {
    if (*p == ':') {
      *p = 0;
      eyecmd_printf(q);
      fprintf(stderr, "%s: eyelink_opt=<%s>\n", progname, q);
      *p = ':';
      q = p + 1;
    }
  }

  /* this should be "0" or "1", default to 1 */
  p = getenv("XXEYELINK_CAMERA");
  if (p == NULL || sscanf(p, "%d", &eyelink_camera) != 1) {
    eyelink_camera = 1;
  }
  sprintf(buf, "eyelink_camera = %d", eyelink_camera);
  fprintf(stderr, "%s: %s\n", progname, buf);
  eyecmd_printf(buf);

  /* Tue Jan 17 11:37:48 2006 mazer 
   * if file "eyelink.ini" exists in the current directory, send
   * it as a series of commands to the eyelink over the network.
   */

  if ((fp = fopen("eyelink.ini", "r")) != NULL) {
    while (fgets(buf, sizeof(buf), fp) != NULL) {
      if ((p = index(buf, '\n')) != NULL) {
	*p = 0;
      }
      fprintf(stderr, "%s: %s\n", progname, buf);
      eyecmd_printf(buf);
    }
  }

  // start recording & tell EL to send samples but
  // not events through link
  p = getenv("EYELINK_FILE");
  if (p != NULL) {
    open_data_file(p);
    if (start_recording(1,1,1,0)) {
      fprintf(stderr, "%s/eyelink_init: can't start recording\n", progname);
      return;
    }
    fprintf(stderr, "%s/eyelink_init: saving data to '%s'\n", progname, p);
  } else {
    if (start_recording(0,0,1,0)) {
      fprintf(stderr, "%s/eyelink_init: can't start recording\n", progname);
      return;
    }
  }

  if (eyelink_wait_for_block_start(10,1,0)==0) {
    fprintf(stderr, "%s/eyelink_init: can't get block start\n", progname);
    return;
  }

  fprintf(stderr, "%s/eyelink_init: connected ok\n", progname);
  tracker_mode = EYELINK;
#ifdef CHANGE_NAME
  set_proc_title(saved);
#endif
}


static void eyelink_halt()
{
  char *p;

  if (tracker_mode == EYELINK || tracker_mode == EYELINK_TEST) {
    stop_recording();
    set_offline_mode();
    tracker_mode = ANALOG;

    p = getenv("EYELINK_FILE");
    if (p != NULL) {
      pump_delay(500);
      eyecmd_printf("close_data_file");
      fprintf(stderr, "%s/eyelink_halt: requesting '%s'\n", progname, p);
      if (receive_data_file(p, p, 0) > 1) {
	fprintf(stderr, "%s/eyelink_halt: received.\n", progname);
      } else {
	fprintf(stderr, "%s/eyelink_halt: error receiving.\n", progname);
      }
    }
  }
}

static int eyelink_read(float *x, float *y,  float *p,
			unsigned int *t, int *new)
{
  static FSAMPLE sbuf;
  int e;

  if ((e = eyelink_newest_float_sample(&sbuf)) < 0) {
    return(0);
  } else {
#ifdef DEBUGGING
    fprintf(stderr, "ti = %d\n.", sbuf.time);
    fprintf(stderr, " px = [%f %f]\n", sbuf.px[0], sbuf.px[eyelink_camera]);
    fprintf(stderr, " py = [%f %f]\n", sbuf.py[0], sbuf.py[eyelink_camera]);
    fprintf(stderr, " pa = [%f %f]\n", sbuf.pa[0], sbuf.pa[eyelink_camera]);
#endif /* DEBUGGING */
    /* there are new data about eye positions */
    *t = (unsigned int) sbuf.time;
    *x = sbuf.px[eyelink_camera];		/* xpos, RIGHT/LEFT */
    *y = sbuf.py[eyelink_camera];		/* ypos, RIGHT/LEFT */
    *p = sbuf.pa[eyelink_camera];		/* pupil area, RIGHT/LEFT */
    *new = (e == 1);
    return(1);
  }
}


#define RDTSC(x) __asm__ __volatile__ ( ".byte 0x0f,0x31" \
					:"=a" (((unsigned long*)&x)[0]), \
					 "=d" (((unsigned long*)&x)[1]))

static unsigned long timestamp(int init)
{
  static unsigned long long timezero;
  unsigned long long now;

  RDTSC(now);			/* get cycle counter from hardwareTSC */
  if (init) {
    timezero = now;
    return(0);
  } else {
    /* use precalibrated ticks_per_ms to convert to real time.. */
    return((unsigned long)((now - timezero) / ticks_per_ms));
  }
}

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
  register int i, z, lastpri, setpri;
  register float x, y, pa, tmp, calx, caly;
  float tx, ty, tp;
  unsigned long last_ts = 0, ts;
  unsigned int eyelink_t;
  int eyelink_new;
  int k;
  long accum[NADC], naccum;
  int jsbut, jsnum, jsval;
  unsigned long jstime;

  register float sx=0, sy=0;
  int si, sn;
  float sbx[MAXSMOOTH], sby[MAXSMOOTH];

  /*
   * calx/caly are the gain+offset adjusted eye position values
   * x/y are the raw values
   */
  calx = caly = x = y = pa = -1;

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
    naccum = 0;
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

    if (tracker_mode == ISCAN) {
      x = iscan_x;
      y = iscan_y;
      pa = iscan_p;
    } else if (tracker_mode == EYELINK) {
      /* try reading from eyelink */
      if (eyelink_read(&tx, &ty, &tp, &eyelink_t, &eyelink_new) != 0) {
	x = tx;
	y = ty;
	pa = tp;
      }
    } else if (tracker_mode == EYELINK_TEST) {
      /* try reading from eyelink */
      if (eyelink_read(&tx, &ty, &tp, &eyelink_t, &eyelink_new) == 0) {
	tx = ty = tp = -1;
      }
      LOCK(semid);
      x = dacq_data->adc[0];
      y = dacq_data->adc[1];
      UNLOCK(semid);
    } else {
      x = dacq_data->adc[0];
      y = dacq_data->adc[1];
      pa = -1;
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
    dig_in();

    /* Fri Mar 10 10:05:30 2006 mazer 
     * Check joystick for mock-digital inputs, if joystick's been
     * initialized. Right now this is just a stub...
     */
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
	} else if (jsbut == 0 && jsnum == 1) {
	  /* y-axis motion, jsval indicates the current value */
	}
      }
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

      if (tracker_mode == EYELINK_TEST) {
	/* in test mode, analog channels 0,1,4 are filled with
	 * the eyelink data (x,y,pupil area)
	 */
	dacq_data->adbuf_c0[k] = (int)(tx > 0 ? tx+0.5 : tx-0.5);
	dacq_data->adbuf_c1[k] = (int)(ty > 0 ? ty+0.5 : ty-0.5);
	dacq_data->adbuf_c2[k] = (int)((x > 0) ? (x+0.5) : (x-0.5));
	dacq_data->adbuf_c3[k] = (int)((y > 0) ? (y+0.5) : (y-0.5));
	dacq_data->adbuf_c4[k] = (int)(tp > 0 ? tp+0.5 : tp-0.5);
      } else {
	/* otherwise, the raw analog values are stuffed in, which
	 * are usually raw x,y values off the coil, unless you're
	 * using them for something else (and have iscan/eyelink)
	 */
	dacq_data->adbuf_c0[k] = dacq_data->adc[0];
	dacq_data->adbuf_c1[k] = dacq_data->adc[1];
	dacq_data->adbuf_c2[k] = dacq_data->adc[2];
	dacq_data->adbuf_c3[k] = dacq_data->adc[3];

	/* Mon Jan 16 09:25:34 2006 mazer 
	 *  set up saving EDF-time to c4 channel for debugging

	 dacq_data->adbuf_c4[k] = eyelink_t;

	 */
      }
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

  init();
  fprintf(stderr, "%s: initted\n", progname);

  if (av[1] && (strcmp(av[1], "-eyelink") == 0)) {
    eyelink_init(av[2]);
  } else if (getenv("EYELINK_TEST") != NULL) {
    eyelink_init(getenv("EYELINK_TEST"));
    if (tracker_mode == EYELINK) {
      tracker_mode = EYELINK_TEST;
      fprintf(stderr, "*** eyelink test mode SUCCESS!\n");
    } else {
      fprintf(stderr, "*** eyelink test mode FAILED!\n");
    }
  } else if (ac > 2) {
    iscan_init(av[1], av[2]);
  }

  if (getenv("XXSWAP_XY")) {
    /* this option is useful ONLY if the camera is rotated, like with
     * the original software release for the eyelink ELCL...
     */
    swap_xy = 1;
    fprintf(stderr, "%s: swapping X and Y\n", progname);
  }

  if ((p = getenv("XXUSBJS")) != NULL) {
    usbjs_dev = usbjs_init(p);
    if (usbjs_dev < 0) {
      fprintf(stderr, "%s: can't open joystick %s\n", progname, p);
    } else {
      fprintf(stderr, "%s: joystick at %s configured\n", progname, p);
    }
  }

  mainloop();
  fprintf(stderr, "%s: bye bye\n", progname);
  exit(0);
}

