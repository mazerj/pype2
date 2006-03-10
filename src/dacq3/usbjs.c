/* title:   usbjs.c

** author:  jamie mazer
** created: Thu Mar  9 17:18:53 2006 mazer 
** info:    direct interface for a usb joystick device.
** history:
**
*/

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/capability.h>

#include "usbjs.h"

/* from: kernel.../Documentation/input/joystick-api.txt */

#define JS_EVENT_BUTTON         0x01    /* button pressed/released */
#define JS_EVENT_AXIS           0x02    /* joystick moved */
#define JS_EVENT_INIT           0x80    /* initial state of device */

#define JS_DOWN	1		/* button down event */
#define JS_UP	0		/* button up event */


struct js_event {
  unsigned long time;		/* event timestamp in milliseconds */
  short value;			/* value */
  unsigned char type;		/* event type */
  unsigned char number;		/* axis/button number */
};

int usbjs_init(char *devname)
{
  return(open(devname ? devname : "/dev/input/js0", O_RDONLY|O_NDELAY));
}

void usbjs_close(int fd)
{
  if (fd >= 0) {
    close(fd);
  }
}

int usbjs_query(int fd, int *buttonp, int *number, int *value,
		unsigned long *time)
{
  struct js_event e;

  if (read(fd, &e, sizeof(struct js_event)) < 0) {
    if (errno != EAGAIN) {
      fprintf(stderr, "usbjs_query: read error!\n");
    }
    return(0);
  } else {
    /* consider init and non-init events as the samething... */
    e.type &= ~JS_EVENT_INIT;
    if (buttonp) {
      if (e.type & JS_EVENT_BUTTON) {
	/* button event */
	*buttonp = 1;
      } else {
	/* axis event */
	*buttonp = 0;
      }
    }
    if (number) {
      /* button or axis number */
      *number = e.number;
    }
    if (value) {
      *value = e.value;
    }
    if (time) {
      *time = e.time;
    }
    return(1);
  }
}
