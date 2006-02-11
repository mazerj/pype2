#include <sys/types.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/mman.h>
#include <sys/io.h>

#include "dacqinfo.h"
#include "sigs.h"
#include "debug.h"

//#define BASE	0x3bc		/* /dev/lp0 */
#define BASE	0x378		/* /dev/lp1 */
//#define BASE	0x278		/* /dev/lp2 */


static int base = BASE;


static int init(void)
{
  /* first get access to IO ports -- this requires root perms */
  if (iopl(3) != 0) {
    perror("iopl");
    exit(1);
  }
  return(1);
}

main(int ac, char **av)
{
  unsigned char x, y, lx, ly;
  int n;

  if (ac > 1) {
    sscanf(av[1], "%x", &base);
  }

  init();

  printf("base=0x%03x\n", base);


  lx = ly = 0;
  while (1) {
    x = inb(base + 1);
    if (lx != x || ly != y) {
      printf("0x%03x: ", base);

      for (n = 0; n < 8; n++) {
	printf("%d", 7-n);
      }
      printf(" ");
      for (n = 0; n < 8; n++) {
	printf("%d", ((1<<(7-n)) & x) ? 1 : 0);
      }
      printf("\n");
      fflush(stdout);
      lx = x;
      ly = y;
    }

  }
}

