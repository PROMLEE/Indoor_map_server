import os
import cv2
import numpy as np
from glob import glob
from scipy.io import loadmat
import matplotlib.pyplot as plt
import pickle
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


os.environ["CUDA_VISIBLE_DEVICES"] = "0"

IMAGE_SIZE = 512
BATCH_SIZE = 1
NUM_CLASSES = 3
DATA_DIR1 = "./Training"
DATA_DIR2 = "./Validation"

# train_images = sorted(glob(os.path.join(DATA_DIR1, "images/*")))
# train_masks = sorted(glob(os.path.join(DATA_DIR1, "mask_images/*")))

# val_images = sorted(glob(os.path.join(DATA_DIR2, "images/*")))
# val_masks = sorted(glob(os.path.join(DATA_DIR2, "mask_images/*")))

train_images = sorted(glob(os.path.join("sources\CAU208", "images/*")))
train_masks = sorted(glob(os.path.join(DATA_DIR1, "mask_images/*")))

val_images = sorted(glob(os.path.join(DATA_DIR2, "images/*")))
val_masks = sorted(glob(os.path.join(DATA_DIR2, "mask_images/*")))


def read_image(image_path, mask=False):
    image = tf.io.read_file(image_path)
    if mask:
        # 마스크 이미지를 로드합니다. 이 때, 클래스 인덱스는 정수여야 합니다.
        image = tf.image.decode_png(image, channels=1)
        image.set_shape([None, None, 1])
        image = tf.image.resize(
            images=image,
            size=[IMAGE_SIZE, IMAGE_SIZE],
            method=tf.image.ResizeMethod.NEAREST_NEIGHBOR,
        )  # resizing method 변경
        image = tf.cast(image, tf.int32)  # 중요: 라벨은 정수 형태여야 합니다.
        image = tf.squeeze(image, axis=-1)
    else:
        image = tf.image.decode_png(image, channels=3)
        image.set_shape([None, None, 3])
        image = tf.image.resize(images=image, size=[IMAGE_SIZE, IMAGE_SIZE])
        image = image / 127.5 - 1

    return image


# def load_data(image_list, mask_list):
#     image = read_image(image_list)
#     mask = read_image(mask_list, mask=True)
#     return image, mask


# def data_generator(image_list, mask_list):
#     dataset = tf.data.Dataset.from_tensor_slices((image_list, mask_list))
#     dataset = dataset.map(load_data, num_parallel_calls=tf.data.AUTOTUNE)
#     dataset = dataset.batch(BATCH_SIZE, drop_remainder=True)
#     return dataset


# train_dataset = data_generator(train_images, train_masks)
# val_dataset = data_generator(val_images, val_masks)

# print("Train Dataset: ", train_dataset)
# print("Val Dataset: ", val_dataset)


# def convolution_block(
#     block_input,
#     num_filters=256,
#     kernel_size=3,
#     dilation_rate=1,
#     padding="same",
#     use_bias=False,
# ):
#     x = layers.Conv2D(
#         num_filters,
#         kernel_size=kernel_size,
#         dilation_rate=dilation_rate,
#         padding="same",
#         use_bias=use_bias,
#         kernel_initializer=keras.initializers.HeNormal(),
#     )(block_input)
#     x = layers.BatchNormalization()(x)
#     return tf.nn.relu(x)


# def DilatedSpatialPyramidPooling(dspp_input):
#     dims = dspp_input.shape
#     x = layers.AveragePooling2D(pool_size=(dims[-3], dims[-2]))(dspp_input)
#     x = convolution_block(x, kernel_size=1, use_bias=True)
#     out_pool = layers.UpSampling2D(
#         size=(dims[-3] // x.shape[1], dims[-2] // x.shape[2]), interpolation="bilinear"
#     )(x)
#     out_1 = convolution_block(dspp_input, kernel_size=1, dilation_rate=1)
#     out_6 = convolution_block(dspp_input, kernel_size=3, dilation_rate=6)
#     out_12 = convolution_block(dspp_input, kernel_size=3, dilation_rate=12)
#     out_18 = convolution_block(dspp_input, kernel_size=3, dilation_rate=18)

#     x = layers.Concatenate(axis=-1)([out_pool, out_1, out_6, out_12, out_18])
#     output = convolution_block(x, kernel_size=1)
#     print(output)
#     return output


# def DeeplabV3Plus(image_size, num_classes):
#     # DeeplabV3+ with ResNet50 backbone
#     model_input = keras.Input(shape=(image_size, image_size, 3))

#     # Encoder: ResNet50
#     resnet50 = keras.applications.ResNet50(
#         weights="imagenet", include_top=False, input_tensor=model_input
#     )

#     # Extract feature from the last layer of stage 4
#     low_level_features = resnet50.get_layer("conv4_block6_2_relu").output
#     high_level_features = resnet50.get_layer(
#         "conv5_block3_2_relu"
#     ).output  # it was previously "conv4_block6_2_relu"

#     # High-level feature extractor - Atrous Spatial Pyramid Pooling
#     x = DilatedSpatialPyramidPooling(high_level_features)

#     low_level_features = layers.Conv2D(
#         filters=48,
#         kernel_size=(1, 1),
#         padding="same",
#         kernel_initializer="he_normal",
#         name="low_level_features",
#     )(low_level_features)
#     low_level_features = layers.BatchNormalization()(low_level_features)
#     low_level_features = layers.Activation(tf.nn.relu)(low_level_features)

#     low_level_features = layers.UpSampling2D(size=(2, 2), interpolation="bilinear")(
#         low_level_features
#     )  # 수정된 부분

#     # Upsampling and concatenating high-level and low-level features
#     x = layers.UpSampling2D(size=(4, 4), interpolation="bilinear")(x)
#     x = layers.Concatenate()([x, low_level_features])

#     # Decoder: 3x3 convolutions with batch normalization and ReLU
#     x = layers.Conv2D(
#         filters=256,
#         kernel_size=(3, 3),
#         padding="same",
#         kernel_initializer="he_normal",
#         name="decoder_conv1",
#     )(x)
#     x = layers.BatchNormalization()(x)
#     x = layers.Activation(tf.nn.relu)(x)

#     x = layers.Conv2D(
#         filters=256,
#         kernel_size=(3, 3),
#         padding="same",
#         kernel_initializer="he_normal",
#         name="decoder_conv2",
#     )(x)
#     x = layers.BatchNormalization()(x)
#     x = layers.Activation(tf.nn.relu)(x)

#     # Upsample the final feature map to the original input size
#     x = layers.UpSampling2D(size=(8, 8))(x)  # 이 부분이 중요합니다. 여기서 출력 크기를 두 배로 확장합니다.

#     model_output = layers.Conv2D(num_classes, (1, 1), padding="same")(x)

#     # Create the model
#     return keras.Model(inputs=model_input, outputs=model_output)


# model = DeeplabV3Plus(image_size=IMAGE_SIZE, num_classes=NUM_CLASSES)

# model.summary()


# loss = keras.losses.SparseCategoricalCrossentropy(from_logits=True)
# optimizer = keras.optimizers.Adam(learning_rate=0.0001)
# model.compile(
#     optimizer=optimizer,
#     loss=loss,
#     metrics=["accuracy"],
# )
# history = model.fit(train_dataset, validation_data=val_dataset, epochs=20).history

# model.save("example.h5")

# with open("Dict.txt", "wb") as file_pi:
#     pickle.dump(history, file_pi)


model = tf.keras.models.load_model("scripts\example.h5")
history = pickle.load(open("scripts\Dict.txt", "rb"))

loss = history["loss"]
val_loss = history["val_loss"]

fig = plt.figure(figsize=(12, 5))

ax1 = fig.add_subplot(1, 2, 1)
ax1.plot(loss, color="blue", label="train_loss")
ax1.plot(val_loss, color="red", label="val_loss")
ax1.set_title("Train and Validation Loss")
ax1.set_xlabel("Epochs")
ax1.set_ylabel("Loss")
ax1.grid()
ax1.legend()


accuracy = history["accuracy"]
val_accuracy = history["val_accuracy"]

ax2 = fig.add_subplot(1, 2, 2)
ax2.plot(accuracy, color="blue", label="train_Accuracy")
ax2.plot(val_accuracy, color="red", label="val_Accuracy")
ax2.set_title("Train and Validation Accuracy")
ax2.set_xlabel("Epochs")
ax2.set_ylabel("Accuracy")
ax2.grid()
ax2.legend()

plt.show()

colormap = loadmat("scripts\matlab.mat")["colormap"]
colormap = colormap * 100
colormap = colormap.astype(np.uint8)


def infer(model, image_tensor):
    predictions = model.predict(np.expand_dims((image_tensor), axis=0))
    predictions = np.squeeze(predictions)
    predictions = np.argmax(predictions, axis=2)
    return predictions


def decode_segmentaion_masks(mask, colormap, n_classes):
    r = np.zeros_like(mask).astype(np.uint8)
    g = np.zeros_like(mask).astype(np.uint8)
    b = np.zeros_like(mask).astype(np.uint8)
    for i in range(0, n_classes):
        idx = mask == i
        r[idx] = colormap[i, 0]
        g[idx] = colormap[i, 1]
        b[idx] = colormap[i, 2]
    rgb = np.stack([r, g, b], axis=2)
    return rgb


def get_overlay(image, colored_mask):
    image = tf.keras.preprocessing.image.array_to_img(image)
    image = np.array(image).astype(np.uint8)
    overlay = cv2.addWeighted(image, 0.35, colored_mask, 0.65, 0)
    return overlay


def plot_samples_matplotlib(display_list, figsize=(5, 3)):
    _, axes = plt.subplots(nrows=1, ncols=len(display_list), figsize=figsize)
    for i in range(len(display_list)):
        if display_list[i].shape[-1] == 3:
            axes[i].imshow(tf.keras.preprocessing.image.array_to_img(display_list[i]))
        else:
            axes[i].imshow(display_list[i])
    plt.show()


def plot_predictions(images_list, colormap, model):
    for image_file in images_list:
        image_tensor = read_image(image_file)
        prediction_mask = infer(image_tensor=image_tensor, model=model)
        prediction_colormap = decode_segmentaion_masks(prediction_mask, colormap, 20)
        overlay = get_overlay(image_tensor, prediction_colormap)
        plot_samples_matplotlib(
            [image_tensor, overlay, prediction_colormap], figsize=(18, 14)
        )


plot_predictions(train_images, colormap, model=model)
