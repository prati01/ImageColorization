from keras.applications import VGG16
from keras.engine import Model

from keras import backend as K, Input
from keras import optimizers
from keras.layers import Conv2D, Lambda, Dense, concatenate, regularizers, add, Conv2DTranspose, MaxPooling2D, \
    UpSampling2D

from src.test.test import color_images_full

b_size = 32
input_shape = (224, 224, 3)

weights = "data/weights/vgg.h5"
color_fun = color_images_full
name = "reg_full_vgg_"

def model():
    # VGG
    vgg16 = VGG16(weights="imagenet", include_top=False, input_shape=input_shape)

    # freeze vgg16
    for layer in vgg16.layers:
        layer.trainable = False

    last = UpSampling2D(size=(2, 2))(vgg16.output)
    last = Conv2D(256, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)
    last = Conv2D(256, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)

    last = UpSampling2D(size=(2, 2))(last)
    last = Conv2D(128, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)
    last = Conv2D(128, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)

    last = UpSampling2D(size=(2, 2))(last)
    last = Conv2D(64, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)
    last = Conv2D(64, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)

    last = UpSampling2D(size=(2, 2))(last)
    last = Conv2D(32, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)
    last = Conv2D(2, (3, 3), padding="same", activation="relu", kernel_regularizer=regularizers.l2(0.01))(last)

    def resize_image(x):
        return K.resize_images(x, 2, 2, "channels_last")

    def unormalise(x):
        # outputs in range [0, 1] resized to range [-100, 100]
        return (x * 200) - 100

    last = Lambda(resize_image)(last)
    last = Lambda(unormalise)(last)

    def custom_mse(y_true, y_pred):
        return K.mean(K.square(y_pred - y_true), axis=[1, 2, 3])

    model = Model(inputs=vgg16.input, output=last)
    opt = optimizers.Adam(lr=1E-4, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    model.compile(optimizer=opt, loss=custom_mse)

    model.summary()

    return model

