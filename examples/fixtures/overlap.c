/* Fixture source for cross-tool consensus tests.
   Deliberately flawed so that flawfinder AND cppcheck both flag the SAME line
   with the SAME CWE class — the cross-tool agreement case. Not production code.

   The SARIF fixtures beside this file are CAPTURED from real runs of:
     flawfinder --sarif examples/fixtures/overlap.c
     cppcheck --enable=all --xml --xml-version=2 examples/fixtures/overlap.c
   Do not hand-author them; regenerate with examples/fixtures/regen_fixtures.sh
*/
#include <string.h>
#include <stdio.h>

void overflow_fixed(void) {
    char buf[4];
    strcpy(buf, "aaaaaaaaaaaaaaaa");   /* both tools: buffer overflow (class buf) */
}

void fmt(char *s) {
    printf(s);                          /* flawfinder CWE-134 (class fmt) */
}
