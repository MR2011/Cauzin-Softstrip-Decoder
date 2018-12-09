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
import random
import scipy.misc
from collections import Counter

IMG_FOLDER = "data/row_manual_left"
MODEL_FILENAME = "nn/models/keras_rowtest.hdf5"
MODEL_JSON = "nn/models/keras_rowtest.json"
MODEL_LABELS_FILENAME = "nn/models/keras_row_labelstest.dat"

def oversampling(X, y, filter_threshold=0):
    x_samples = []
    y_samples = []
    y_unique = set(y)
    indices = {}
    for item in y_unique:
        indices[item] = [i for i, x in enumerate(y) if x == item]
    counts = Counter(y)
    max_count = counts.most_common(1)[0][1]
    remove = []
    remove_key = []
    for key, value in counts.items():
        if value < filter_threshold:
            remove += indices[key]
            remove_key.append(key)
    for k in remove_key:
        del counts[k]
    
    for index in sorted(remove, reverse=True):
        del X[index]
        del y[index]
    y_unique = counts.keys()
    for item in y_unique:
        indices[item] = [i for i, x in enumerate(y) if x == item]
    for key, value in counts.items():
        for i in range((max_count - value)):
            index = random.choice(indices[key])
            x_samples.append(X[index])
            y_samples.append(y[index])
    X = X + x_samples
    y = y + y_samples
    counts = Counter(y)
    print(counts)
    return X, y


data = []
labels = []
for image_file in paths.list_images(IMG_FOLDER):
    image = cv2.imread(image_file)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = scipy.misc.imresize(image, [20, 10])
    image = np.expand_dims(image, axis=2)
    y = int(image_file.split(os.path.sep)[-1].split('_')[1].split('.')[0])
    data.append(image)
    labels.append(y)

X_resampled, y_resampled = oversampling(data, labels, 10)
X_resampled = np.array(X_resampled) / 255.0
y_resampled = np.array(y_resampled)


(X_train, X_test, Y_train, Y_test) = train_test_split(X_resampled, y_resampled, test_size=0.25, random_state=0)
lb = LabelBinarizer().fit(Y_train)
Y_train = lb.transform(Y_train)
Y_test = lb.transform(Y_test)

with open(MODEL_LABELS_FILENAME, "wb") as f:
    pickle.dump(lb, f)


model = Sequential()


model.add(Conv2D(64, (5, 5), padding="same", input_shape=(20, 10, 1), activation="relu"))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
model.add(Conv2D(128, (5, 5), padding="same", activation="relu"))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
model.add(Flatten())
model.add(Dense(500, activation="relu"))
model.add(Dense(250, activation="relu"))
model.add(Dense(5, activation="softmax"))
model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

EPOCHS = 50

H = model.fit(X_train, Y_train, validation_data=(X_test, Y_test), batch_size=32, epochs=EPOCHS, verbose=1)

model_json = model.to_json()
model.summary()
with open(MODEL_JSON, "w") as json_file:
    json_file.write(model_json)
model.save_weights(MODEL_FILENAME)

