import numpy as np
import imageio
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import random
import os

def ReadImage(path_to_image):

    f = imageio.imread(path_to_image)

    return f

def ShowImage(image):
    plt.imshow(image)
    plt.show()

def ClassifyImage(image, class_images):
    
    pieces = FindPieces(image)
    n_pieces = len(pieces)
    classifier = list()

    for k in range(n_pieces):
        piece = pieces[k]
        classifier[k] = ClassifyPiece(piece)

    return classifier

def FindPieces(image):
    
    pieces = list()

    return pieces

def FindClassifyImages(path_to_class):
    
    filenames = os.listdir(path_to_class)
    n_classes = len(filenames)
    class_images = list()
    
    for k in range(n_classes):
        tmp_path = path_to_class + filenames[k]
        class_images.append(imageio.imread(tmp_path))

    return class_images

def ClassifyPiece(piece):

    classifier = list()

    return classifier


dirname = os.path.dirname(__file__)

path_to_image = os.path.join(dirname, 'eternityNumbering.png')
path_to_class = os.path.join(dirname, 'Classes/')

image = ReadImage(path_to_image)
class_images = FindClassifyImages(path_to_class)

ShowImage(image)

ClassifyImage(image, class_images)
