/* title:   eyelink.c

** author:  jamie mazer
** created: Thu Dec 18 11:41:01 2008 mazer 
** info:    eyelink interface code
** history:
**
** Thu Dec 18 11:40:34 2008 mazer 
**   - split out from das_common.c
**
** Tue May  5 16:26:16 2009 mazer 
**   - changed private XXxxx env vars to XX_xxxx
*/


/* these are eyelink API header files */
#include "eyelink.h"
#include "eyetypes.h"

/* this has set_eyelink_address() etc.. */
#include "exptsppt.h"

static int eyelink_camera = -1;

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

  /* 16-apr-2003: step through the XX_EYELINK_OPTS env var (commands
   * separated by :'s) and set each command to the eyelink, while
   * echoing to the console..  This variable is setup by pype before
   * dacq_start() gets called..
   */
  opts = getenv("XX_EYELINK_OPTS");
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
  p = getenv("XX_EYELINK_CAMERA");
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

  if (tracker_mode == EYELINK) {
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


