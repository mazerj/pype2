#include <stdio.h>		/* for stderr() */
#include <unistd.h>		/* for geteuid() */
#include <stdlib.h>		/* for exit() */

main(int ac, char **av)
{
  if (geteuid() != 0) {
    fprintf(stderr, "pypeboot: not suid root and not running as root.\n");
    exit(1);
  } else {
    execvp(av[1], av+1);
  }
}
