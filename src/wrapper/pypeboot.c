#include <stdio.h>
#include <unistd.h>

main(int ac, char **av)
{
  execvp(av[1], av+1);
}
