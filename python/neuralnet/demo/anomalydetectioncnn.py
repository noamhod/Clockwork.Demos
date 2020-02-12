#!/usr/bin/env python
import keras
from keras import optimizers
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers import LeakyReLU
from keras import metrics
from sklearn.model_selection import train_test_split

from keras.utils import to_categorical
from sklearn.preprocessing import LabelBinarizer

from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import argparse
import random
import cv2
import os

############################################################
### supress tensorflow warnings 
import logging
logging.getLogger('tensorflow').disabled = True
# Just disables the warning, doesn't enable AVX/FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
############################################################


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True, help="path to input dataset of images")
# ap.add_argument("-e", "--epochs", required=True, help="number of epochs for the training")
args = vars(ap.parse_args())

# initialize the data and labels
print("[INFO] loading images...")
data = []
labels = []

# # grab the image paths and randomly shuffle them
# imagePaths = sorted(list(paths.list_images(args["dataset"])))
# random.seed(42)
# random.shuffle(imagePaths)
# 
# # loop over the input images
# for imagePath in imagePaths:
# 	# load the image, resize the image to be 32x32 pixels (ignoring
# 	# aspect ratio), flatten the image into 32x32x3=3072 pixel image
# 	# into a list, and store the image in the data list
# 	image = cv2.imread(imagePath)
# 	# image = cv2.resize(image, (32, 32)).flatten()
# 	image = cv2.resize(image, (96, 96)).flatten()
# 	data.append(image)
# 
# 	# extract the class label from the image path and update the
# 	# labels list
# 	label = imagePath.split(os.path.sep)[-2]
# 	labels.append(label)
# ### transform to numpy arrays
# data = np.array(data, dtype="float") / 255.0 # scale the raw pixel intensities to the range [0, 1]
# labels = np.array(labels)

from PIL import Image
import os
import glob
toys = glob.glob(args["dataset"]+"/*.png")
Ntoys = len(toys)
print "Found %g good toy files" % Ntoys
for f in toys:
   img = Image.open(f)
   img.load()
   # image = np.asarray(img, dtype="float") / 255.
   image = np.asarray(img, dtype="int32")
   data.append(image)
   labels.append(0)
data = np.array(data)
labels = np.array(labels)
# print data.shape


# partition the data into training and testing splits using 70% of
# the data for training and the remaining 30% for testing
(images_train, images_test, labels_train, labels_test) = train_test_split(data, labels, test_size=0.3, random_state=42)


# lb = LabelBinarizer()
# images_train = lb.fit_transform(images_train)
# images_train = to_categorical(images_train) ########### If your targets are integer classes, you can convert them to the expected format via


## input data parameters
# IMAGES_SHAPE = (96, 96, 4)
IMAGES_SHAPE = (480, 640, 4)
PADDING = 'same'
KERNEL_SIZE = (5, 5)
KERNEL_INITIALIZER = 'glorot_normal'
# parameters for deep layers
# NUMBER_OF_CLASSES = 3  # N, IR and B
NUMBER_OF_CLASSES = 1
DROPOUT = 0.5
LEAK_ALPHA = 0.1
MAX_POOLING_POOL_SIZE = (2, 2)
ACTIVATION_LAYER_FUNCTION = 'softmax'
# loss and optimizer
# LOSS_FUNCTION = 'categorical_crossentropy'
LOSS_FUNCTION = 'sparse_categorical_crossentropy'
LEARNING_RATE = 0.001
OPTIMIZER = optimizers.Adam(LEARNING_RATE, epsilon=10e-6)


# CNN architecture from Guo et al.
model = Sequential()
model.add(Conv2D(5, KERNEL_SIZE, input_shape=IMAGES_SHAPE, data_format='channels_last', kernel_initializer=KERNEL_INITIALIZER, padding=PADDING))
model.add(LeakyReLU(LEAK_ALPHA))
model.add(Conv2D(10, KERNEL_SIZE, kernel_initializer=KERNEL_INITIALIZER, padding=PADDING))
model.add(LeakyReLU(LEAK_ALPHA))
model.add(MaxPooling2D(pool_size=MAX_POOLING_POOL_SIZE))
model.add(Conv2D(10, KERNEL_SIZE, kernel_initializer=KERNEL_INITIALIZER, padding=PADDING))
model.add(LeakyReLU(LEAK_ALPHA))
model.add(MaxPooling2D(pool_size=MAX_POOLING_POOL_SIZE))
model.add(Flatten())
model.add(Dense(10))
model.add(LeakyReLU(LEAK_ALPHA))
model.add(Dense(5))
model.add(LeakyReLU(LEAK_ALPHA))
model.add(Dropout(DROPOUT))
model.add(Dense(NUMBER_OF_CLASSES))
model.add(Activation(ACTIVATION_LAYER_FUNCTION))
  

model.compile(loss=LOSS_FUNCTION, optimizer=OPTIMIZER, metrics=[metrics.categorical_accuracy])  
model.summary()


BATCH_SIZE = 64
NUMBER_OF_EPOCHS = 5
VALIDATION_SPLIT = 0.25
history = model.fit(images_train, labels_train, batch_size=BATCH_SIZE, epochs=NUMBER_OF_EPOCHS, validation_split=VALIDATION_SPLIT, verbose=1)

### test the CNN
labels_predicted = history.model.predict_classes(images_test, verbose=1)
# for the confusion matrix we need a factorized labels 
# [1,0,0] -> 0 ("N")
# [0,1,0] -> 1 ("IR")
# [0,0,1] -> 2 ("B")
labels_test_factorized = [(1*label[0]+2*label[1]+3*label[2])-1 for label in labels_test_onehot]
from sklearn.metrics import classification_report
print(classification_report(labels_test_factorized, labels_predicted))
