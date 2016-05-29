#!/bin/bash

# Start a simple http stream (ogg vorbis) on port 8000
# Not very low latency so it takes a while from a frequency change
# until you actually hear it.

gst-launch-1.0 alsasrc ! "audio/x-raw, format=S16LE,rate=44100,channels=1" ! audioconvert ! vorbisenc quality=0.9 ! oggmux ! tcpserversink host=0.0.0.0 port=8000 blocksize=1300

