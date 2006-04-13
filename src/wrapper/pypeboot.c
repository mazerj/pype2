#include <stdio.h>
#include <unistd.h>

main(int ac, char **av)
{
  if (geteuid() != 0) {
    fprintf(stderr, "pypeboot: not suid root and not running as root.\n");
    exit(1);
  } else {
    execvp(av[1], av+1);
  }
}
