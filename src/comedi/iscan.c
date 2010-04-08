/* title:   iscan.c

** author:  jamie mazer
** created: Thu Dec 18 11:41:01 2008 mazer 
** info:    iscan interface code
** history:
**
** Thu Dec 18 11:40:34 2008 mazer 
**   - split out from das_common.c
*/


/* ez-serial library for iscan interface */
#include "libezV24-0.0.3/ezV24.h"

static v24_port_t *iscan_port = NULL;

static void iscan_init(char *dev)
{
  if ((iscan_port = v24OpenPort(dev, V24_NO_DELAY | V24_NON_BLOCK)) == NULL) {
    fprintf(stderr, "%s: iscan_init can't open \"%s\"\n.", progname, dev);
    exit(1);
  }
  v24SetParameters(iscan_port, V24_B115200, V24_8BIT, V24_NONE);

  tracker_mode = ISCAN;
  fprintf(stderr, "%s: opened iscan_port (%s)\n", progname, dev);
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

  // 2 bytes/param; 2 params/packet ==> 4 bytes/packet (XP, YP, XCR, YCR)
  int packet_length = 8;

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
    if (bp == (packet_length - 1)) {
      if (ibuf[0] || ibuf[1] || ibuf[2] || ibuf[3]) {
	// currently packets should be:
	///   <PUP_H1 PUP_V1 CR_H1 CR_V1>
	iscan_x = (ibuf[0] - ibuf[2] + 4096);
	iscan_y = (ibuf[1] - ibuf[3] + 4096);
	iscan_p = 1000;
	//fprintf(stderr, "  x=%d y=%d\n", iscan_x, iscan_y); fflush(stderr);
	return;
      } else {
	// out of range or no pupil lock
	iscan_x = 99999;
	iscan_y = 99999;
	iscan_p = 0;
	//fprintf(stderr, "* x=%d y=%d\n", iscan_x, iscan_y); fflush(stderr);
	return;
      }
    } else {
      if (++bp > (packet_length - 1)) {
	fprintf(stderr, "something bad happened.\n");
      }
    }
  }
}
