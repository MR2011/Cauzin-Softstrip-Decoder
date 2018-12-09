import cv2
import pickle
import os.path
import numpy as np
from imutils import paths
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.core import Flatten, Dense

from keras.constraints import maxnorm
import scipy.misc
from keras.layers.core import Dropout

from keras.layers import BatchNormalization

IMG_FOLDER = "data/extracted_first_strip"
MODEL_FILENAME = "nn/models/cauzin_test.hdf5"
MODEL_JSON = "nn/models/cauzin_test.json"
MODEL_LABELS_FILENAME = "nn/models/cauzin_test_labels.dat"


data = []
labels = []

for image_file in paths.list_images(IMG_FOLDER):
    image = cv2.imread(image_file)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = scipy.misc.imresize(image, [20, 20])

    image = np.expand_dims(image, axis=2)

    label = image_file.split(os.path.sep)[-1].split('.')[0][0:2]

    data.append(image)
    labels.append(label)

data = np.array(data) / 255.0
labels = np.array(labels)


(X_train, X_test, Y_train, Y_test) = train_test_split(data, labels, test_size=0.25, random_state=0)


lb = LabelBinarizer().fit(Y_train)
Y_train = lb.transform(Y_train)
Y_test = lb.transform(Y_test)


with open(MODEL_LABELS_FILENAME, "wb") as f:
    pickle.dump(lb, f)


model = Sequential()
model.add(Conv2D(1, (3, 3), input_shape=(20, 20, 1),  padding="same", activation="relu", kernel_constraint=maxnorm(3)))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
model.add(Dropout(0.5))
model.add(BatchNormalization())
model.add(Flatten())
model.add(Dense(1, activation="sigmoid"))
model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

EPOCHS = 3

H = model.fit(X_train, Y_train, validation_data=(X_test, Y_test), batch_size=32, epochs=EPOCHS, verbose=1)

model_json = model.to_json()
with open(MODEL_JSON, "w") as json_file:
    json_file.write(model_json)

model.save_weights(MODEL_FILENAME)

