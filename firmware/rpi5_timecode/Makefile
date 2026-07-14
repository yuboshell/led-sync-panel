CC      = gcc
CFLAGS  = -Wall -O2

all: blink timecode

blink: blink.c
	$(CC) $(CFLAGS) -o blink blink.c

timecode: main.c
	$(CC) $(CFLAGS) -o timecode main.c

clean:
	rm -f blink timecode
