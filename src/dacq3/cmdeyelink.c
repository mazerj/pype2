/* title:   

** author:  jamie mazer
** created: Thu Mar 20 15:17:28 2003 mazer 
** info:    
** history:
**
**
*/

#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/errno.h>
#include <sys/resource.h>

/* these are eyelink API header files */
#include "eyelink.h"
#include "eyetypes.h"

void eyelink_init(char *ip_address)
{
  char buf[100];
  int i;

  fprintf(stderr, "eyelink_init: trying %s\n", ip_address);
  set_eyelink_address(ip_address);
  
  if (open_eyelink_connection(0)) {
    fprintf(stderr, "\neyelink_init: can't open connection to tracker\n");
    return;
  }
  i = eyelink_get_tracker_version(buf);
  fprintf(stderr, "(%d) %s\n", i, buf);
  //set_offline_mode();
  //eyecmd_printf("active_eye = right");
}


void eyelink_halt()
{
  //stop_recording();
  //set_offline_mode();
  close_eyelink_connection();
}

int main(int ac, char **av)
{
  int r;

  if (ac < 1) {
    fprintf(stderr, "usage: cmdeyelink ipnum [filename]\n");
    exit(1);
  }
  eyelink_init(av[1]);
  r = open_data_file(av[2]);
  eyelink_halt();
  fprintf(stderr, "(%d) opened file: %s\n", r, av[2]);

  exit(0);
}
