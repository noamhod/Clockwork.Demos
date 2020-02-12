#!/usr/bin/env python
from PIL import Image
import numpy as np
import os
import glob


toys = glob.glob("/Users/hod/cernbox/tests/bkg/*.png")
Ntoys = len(toys)
print "Found %g good toy files" % Ntoys

x = []
for f in toys:
   img = Image.open(f)
   img.load()
   data = np.asarray(img, dtype="float") / 255.
   x.append(data)
x = np.array(x)
print x.shape