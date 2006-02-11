/* title:   dacqinfo.h
** author:  jamie mazer
** created: Wed Jan  6 23:14:57 1999 mazer 
** info:    generic dacq interface structure
** history:
**
** Wed Jan  6 23:15:08 1999 mazer 
**   This is a generalized version of the original das_server.h
**   file.  The idea is to encapsulate a more general purpose
**   driver abstraction, not so directly tied to the das1600's
**   capabilities.  New devices will be able to use the same
**   interface.
**
** Thu Jan  6 11:14:34 2000 mazer
**   added adc_gain & adc_offset support
**
** Tue May 16 20:43:40 2000 mazer 
**   added support for ISCAN via serial input
**
** Sun Mar  9 13:21:02 2003 mazer 
**   Added din_changes[] to DACQINFO structure to act as latches
**   on the digital input lines.
**
** Mon Jan 23 10:01:22 2006 mazer 
**   Added FIXWIN.vbias for vertical elongation of the fixation window.
*/

#define SHMKEY	0xDA01
#define SEMKEY	0xF0F0

#define NDIGIN	8
#define NDIGOUT	8
#define NADC	4
#define NDAC	2
#define NFIXWIN	1
#define ADBUFLEN (1000 * 60)
#define MAXSMOOTH 25

/* pseudo-interupt codes */
#define INT_DIN		1
#define INT_FIXWIN	2

typedef struct {
  int active;			/* active or idle flag */
  int xchn, ychn;		/* channels to read */
  int cx, cy;			/* center of window */
  float vbias;			/* vertical elongation factor */
  int rad2;			/* window radius ^ 2 (squared for speed) */
  int state;			/* current state (1 for inside) */
  int broke;			/* latched state */
  long break_time;		/* timestamp for last break */
  int fcount;			/* internal.. */
  int nout;			/* internal.. */
  int genint;			/* generate an SIGUSR2 on break?? */
} FIXWIN;

typedef struct {
  /* raw data (input and output) */
  char	din[NDIGIN];		/* status of digital input lines */
  char	din_changes[NDIGIN];	/* # of changes since last reset */
  char  din_intmask[NDIGIN];	/* mask for SIGUSR1 digital inputs */
  char	dout[NDIGOUT];		/* status of digital output lines */
  char	dout_strobe;		/* software strobe (force digital output) */

  int	eye_x;			/* current eye position: X position */
  int	eye_y;			/* current eye position: Y position */
  int	eye_pa;			/* current pupil area, if available */

  /* iscan_[xy] values are maintained continuously
  ** by the iscan_server.c module
  */
  int	iscan_x;		/* last iscan value: X position */
  int	iscan_y;		/* last iscan value: Y position */

  int	adc[NADC];		/* current values for ADC channels */
  int	dac[NDAC];		/* current values for DAC channels */
  int	dac_strobe;		/* software strobe (force DA output) */

  float eye_xgain, eye_ygain;	/* mult. gain for x/y eye position */
  int	eye_xoff, eye_yoff;	/* additive offset in pixels */
  float eye_smooth;		/* NOT IMPLEMENTED NOW */

  /* housekeeping flags */
  unsigned long timestamp;	/* timestamp of last update (ms resolution) */
  int	iscan_terminate;	/* set flag to force iscan termination */
  int	terminate;		/* set flag to force termination */
  int	das_ready;		/* sync flag -- when true, dacq proc ready */
  int	iscan_ready;		/* sync flag -- when true, iscan proc ready */

  /* used only once.. */
  int	dacq_pri;
  int	iscan_pri;

  /* d/a buffers */
  unsigned int	adbuf_on;	/* flag to trigger a/d collect */
  unsigned int	adbuf_ptr;	/* current point in ring buffers */
  unsigned int	adbuf_overflow;	/* overflow flag (INDICATES ERROR!!) */

  unsigned long adbuf_t[ADBUFLEN];	/* timestamps (ms) */
  int		adbuf_x[ADBUFLEN];	/* eye x position trace */
  int		adbuf_y[ADBUFLEN];	/* eye y position trace */
  int		adbuf_pa[ADBUFLEN];	/* pupil area, if available */
  int		adbuf_c0[ADBUFLEN];	/* channel 0/x */
  int		adbuf_c1[ADBUFLEN];	/* channel 1/y */
  int		adbuf_c2[ADBUFLEN];	/* channel 2/photo diode*/
  int		adbuf_c3[ADBUFLEN];	/* channel 3/spike input)*/
  int		adbuf_c4[ADBUFLEN];	/* channel 4/extra analog chanel */

  /* automatic fixation windows */
  FIXWIN fixwin[NFIXWIN];
  int		fixbreak_tau;		/* number of samples outside */
					/* before it counts as a break */

  /* 'interrupt' classes & arguments */
  int int_class;
  int int_arg;
} DACQINFO;

/* these are for backwards compatibility: */
#define adbuf_photo	adbuf_c2
#define adbuf_spikes	adbuf_c3
