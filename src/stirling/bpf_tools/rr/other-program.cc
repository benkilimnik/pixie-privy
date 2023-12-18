#include <stdio.h>
#include <unistd.h>

void Foo() {
  printf("Hello world.\n");
}

// run deterministically e.g. 7 times

int main() {
  // for(;;) {
  for (int i = 0; i < 20; i++) {
    printf("i = %d\n", i);
    sleep(1);
    Foo();
  }
  return 0;
}