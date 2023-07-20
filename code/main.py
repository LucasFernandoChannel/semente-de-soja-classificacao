import tensorflow as tf
from tensorflow.keras import models, layers
import matplotlib.pyplot as plt
import numpy as np

IMAGE_SIZE = 227 # Each image has 227px per 227px
BATCH_SIZE = 32
CHANNELS = 3
EPOCHS = 100
n_classes = 5
input_shape = (BATCH_SIZE, IMAGE_SIZE, IMAGE_SIZE, CHANNELS)
dataPath = "PUT_THE_DATAPATH_HERE"
savePath = "PUT_THE_DIRECTORY_YOU_WISH_TO_SAVE_YOUR_MODEL"

# Load the dataset
dataset = tf.keras.preprocessing.image_dataset_from_directory(
    dataPath,
    shuffle = True,
    image_size = (IMAGE_SIZE, IMAGE_SIZE),
    batch_size = BATCH_SIZE)

dataset_classes = dataset.class_names
print(dataset_classes) # Check if the system loaded the dataset corretly

def split_dataset(dataset, train = 0.7, test = 0.1, validation = 0.2):
  train_size = int(len(dataset) * train) + 1
  test_size = int(len(dataset) * test)

  train_dataset = dataset.take(train_size)
  test = dataset.skip(train_size)
  test_dataset = test.take(test_size)
  validation_dataset = test.skip(test_size)

  return train_dataset, test_dataset, validation_dataset


train_dataset, test_dataset, validation_dataset = split_dataset(dataset)

print(f"Dataset length (numbers of batches): {len(dataset)}")
print(f"Train dataset length (number of batches): {len(train_dataset)}")
print(f"Test dataset length (number of batches): {len(test_dataset)}")
print(f"Validation dataset length (number of batches): {len(validation_dataset)}")

# Define the layers and model
train_dataset = train_dataset.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)
test_dataset = test_dataset.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)
validation_dataset = validation_dataset.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)

resize_and_rescale = tf.keras.Sequential([
    layers.experimental.preprocessing.Resizing(IMAGE_SIZE, IMAGE_SIZE),
    layers.experimental.preprocessing.Rescaling(1.0/255)
])

data_augmentation = tf.keras.Sequential([
    layers.experimental.preprocessing.RandomFlip(mode = "horizontal_and_vertical"),
    layers.experimental.preprocessing.RandomRotation(factor = (0, 1), fill_mode = "wrap"),
    layers.experimental.preprocessing.RandomContrast(factor = (0, 1)),
    layers.experimental.preprocessing.RandomTranslation(height_factor = (0, 1), width_factor = (0, 1), fill_mode = "wrap"),
])

model = models.Sequential([
    resize_and_rescale,
    data_augmentation,
    layers.Conv2D(32, (3, 3), activation = "relu", input_shape = input_shape),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, kernel_size = (3, 3), activation = "relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, kernel_size = (3, 3), activation = "relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, kernel_size = (3, 3), activation = "relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, kernel_size = (3, 3), activation = "relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, kernel_size = (3, 3), activation = "relu"),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(n_classes, activation = "softmax")
])

model.build(input_shape = input_shape)
model.summary()

model.compile(
    optimizer = "adam",
    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits = False),
    metrics = ["accuracy"]
)

model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
    filepath = savePath,
    monitor = "val_accuracy",
    verbose = 1,
    mode = "max",
    save_best_only = True
)

history = model.fit(
    train_dataset,
    epochs = EPOCHS,
    batch_size = BATCH_SIZE,
    verbose = 1,
    validation_data = validation_dataset,
    callbacks = [model_checkpoint]
)

# Evaluate the model
scores = model.evaluate(test_dataset)
acc = history.history["accuracy"]
val_acc = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]

plt.figure(figsize = (8, 8))
plt.subplot(1, 2, 1)
plt.plot(range(EPOCHS), acc, label = "Training accuracy")
plt.plot(range(EPOCHS), val_acc, label = "Validation accuracy")
plt.legend(loc = "lower right")
plt.title("Training and validation accuracy")

plt.subplot(1, 2, 2)
plt.plot(range(EPOCHS), loss, label = "Training loss")
plt.plot(range(EPOCHS), val_loss, label = "Validation loss")
plt.legend(loc = "upper right")
plt.title("Training and validation loss")
plt.show()

# Make a prediction
model = tf.keras.models.load_model(savePath)

for images_batch, labels_batch in test_dataset.take(1):
  first_image = images_batch[0].numpy().astype("uint8")
  first_label = labels_batch[0].numpy()

  print("First image to predict")
  plt.imshow(first_image)
  batch_prediction = model.predict(images_batch)
  print(f"Actual label: {dataset_classes[first_label]}")
  print(f"Prediction: {dataset_classes[np.argmax(batch_prediction[0])]}")
