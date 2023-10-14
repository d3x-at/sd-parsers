#!/bin/bash
# creates wonky png data (Text/EXIF chunk(s) after PNG IDAT)
# use only on jpegs or to create "bad" test images
convert $1 -crop 1x1+0+0 -set filename:d '%d' -set filename:f '%t' -set filename:e '%e' '%[filename:d]/%[filename:f]_cropped.%[filename:e]'
