/* title:   wiimote.c

** author:  jamie mazer
** created: Fri May 21 16:18:32 2010 mazer 
** info:    api for wiimote access (cwiid library)
** history:
**
*/

#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#include <bluetooth/bluetooth.h>
#include <cwiid.h>

#include "wiimote.h"


cwiid_wiimote_t *wiimote_init(char *devname, int *bat)
{
  bdaddr_t ba;
  cwiid_wiimote_t *wii = NULL;
  struct cwiid_state s;

  if (str2ba(devname, &ba) < 0) {
    return(NULL);
  }
  if ((wii = cwiid_connect(&ba, 0)) == NULL) {
    return(NULL);
  }
  cwiid_command(wii, CWIID_CMD_RPT_MODE, 
		CWIID_RPT_CLASSIC | CWIID_RPT_BTN | CWIID_RPT_ACC);
  cwiid_get_state(wii, &s);
  if (bat) {
    *bat = (int)(100.0 * s.battery / CWIID_BATTERY_MAX);
  }
  return(wii);
}

void wiimote_close(cwiid_wiimote_t *wii)
{
  if (wii) {
    cwiid_disconnect(wii);
  }
}

/* button bits:
  bit	key
  1	2
  2	1
  3	B (trigger)
  4	A
  5	-
  6	?
  7	home
  8	left
  9	right
  10	down
  11	up
  12	+
*/

int wiimote_query(cwiid_wiimote_t *wii)
{
  static struct cwiid_state s;
  cwiid_get_state(wii, &s);
  return((int)s.buttons);
}




