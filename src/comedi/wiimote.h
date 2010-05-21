/* title:   wiimote.h

** author:  jamie mazer
** created: Fri May 21 16:18:09 2010 mazer 
** info:    api for wiimote access (cwiid library)
** history:
**
*/

#include <cwiid.h>

cwiid_wiimote_t *wiimote_init(char *devname, int *bat);
extern void wiimote_close(cwiid_wiimote_t *wii);
extern int wiimote_query(cwiid_wiimote_t *wii);
