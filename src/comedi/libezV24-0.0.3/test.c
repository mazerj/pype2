#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>

#include "ezV24.h"

#define BYTE unsigned char

int iscan_read(v24_port_t *port)
{
  static BYTE buf[6];
  static int bp = -1, c;
  int ex, ey;
  int lsb, msb;

  /* initialize the read buffer */
  if (bp < 0) {
    for (bp = 0; bp < sizeof(buf); bp++) {
      buf[bp] = 0;
    }
    bp = 0;
  }

  c = v24Getc(port);
  if (c < 0) {
    for (bp = 0; bp < sizeof(buf); bp++) {
      buf[bp] = 0;
    }
    bp = 0;
    return(0);
  }
  buf[bp] = 0x00ff & c;
  bp = (bp + 1) % sizeof(buf);

  /* check to see if we've got a complete packet */
  if (buf[bp] != 'D' || buf[(bp + 1) % sizeof(buf)] != 'D') {
    /* packet is NOT complete */
    return(0);
  }

  lsb = buf[(bp + 2) % sizeof(buf)];
  msb = buf[(bp + 3) % sizeof(buf)];
  ex = msb;
  ex <<= 8;
  ex |= lsb;
  //ex = ex & 0x0fff;

  printf("0x%02x 0x%02x ", msb, lsb);

  lsb = buf[(bp + 4) % sizeof(buf)];
  msb = buf[(bp + 5) % sizeof(buf)];
  ey = msb;
  ey <<= 8;
  ey |= lsb;
  //ey = ey & 0x0fff;

  if (ex > 0xfff || ex < 0) {
    ex = 0;
  }
  if (ey > 0xfff || ey < 0) {
    ey = 0;
  }

  printf("0x%02x 0x%02x %5d %5d\n", msb, lsb, ex, ey);

  return(1);
}

main()
{
  v24_port_t *port;
  int c, i;

  if ((port = v24OpenPort("/dev/ttyS0",
			  V24_NO_DELAY | V24_NO_DELAY)) == NULL) {
    perror("open");
    exit(1);
  }
  i = v24SetParameters(port, V24_B115200, V24_8BIT, V24_NONE);
  printf("i=%d\n", i);

  v24SetTimeouts(port, 1);

  while (1) {
    iscan_read(port);
  }
  v24ClosePort(port);
}

