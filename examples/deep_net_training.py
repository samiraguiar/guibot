#!/usr/bin/python

# Only needed if not installed system wide
import sys
sys.path.insert(0, '..')


# Program start here
#
# Create a deep network capable of locating a given needle pattern.
# You will need to produce training and testing data as PyTorch tensors
# using the script provided in this project like for instance:
#
#     python misc/generate_pytorch_dataset.py --imglist "train.txt" --isize 150x150 --osize 15x15 --output train.pth
#     python misc/generate_pytorch_dataset.py --imglist "test.txt" --isize 150x150 --osize 15x15 --output test.pth
#
# to produce the data from a list of training or testing image paths and
# location coordinates which could be produced with OpenCV's cascade samples.
# The input and output size parameter have to match those of the configured
# network. This example demonstrated all following steps - network's training,
# testing, configuration, and reuse for a specific matching.

import logging
import shutil

from guibender.settings import GlobalSettings
from guibender.imagelogger import ImageLogger
from guibender.path import Path
from guibender.target import Pattern, Image
from guibender.finder import DeepMatcher
from guibender.errors import *


# parameters to toy with
NEEDLE = 'shape_blue_circle.pth'
HAYSTACK = 'all_shapes'
LOGPATH = './tmp/'
REMOVE_LOGPATH = False
EPOCHS_PER_STAGE = 10
TOTAL_STAGES = 10


# training step
logging.getLogger('').addHandler(logging.StreamHandler())
logging.getLogger('').setLevel(logging.INFO)
finder = DeepMatcher()
# use this to load pretrained model and train futher
#import torch
#weights = torch.load(NEEDLE)
#finder.net.load_state_dict(weights)
# use this to configure
#finder.params["find"]["similarity"].value = 0.7
#finder.params["deep"]["use_cuda"].value = False
#finder.params["deep"]["batch_size"].value = 1000
#finder.params["deep"]["log_interval"].value = 10
#finder.params["deep"]["learning_rate"].value = 0.01
#finder.params["deep"]["sgd_momentum"].value = 0.5
#finder.params["deep"]["iwidth"].value = 150
#finder.params["deep"]["iheight"].value = 150
#finder.params["deep"]["owidth"].value = 15
#finder.params["deep"]["oheight"].value = 15
#finder.params["deep"]["channels_conv1"].value = 10
#finder.params["deep"]["kernel_conv1"].value = 5
#finder.params["deep"]["kernel_pool1"].value = 2
#finder.params["deep"]["channels_conv2"].value = 20
#finder.params["deep"]["kernel_conv2"].value = 5
#finder.params["deep"]["kernel_pool2"].value = 2
#finder.params["deep"]["outputs_linear1"].value = 50
for i in range(EPOCHS_PER_STAGE):
    # train for N epochs saving the obtained needle pattern at each stage
    # (which could also be helpful in case the training is interrupted)
    finder.train(TOTAL_STAGES, 'samples_train.pth', 'targets_train.pth', NEEDLE)
    # test trained network on test samples
    finder.test('samples_test.pth', 'targets_test.pth')


# minimal setup
GlobalSettings.image_logging_level = 0
GlobalSettings.image_logging_destination = LOGPATH
GlobalSettings.image_logging_step_width = 4

path = Path()
path.add_path('images/')

ImageLogger.step = 1

needle = Pattern(NEEDLE)
haystack = Image(HAYSTACK)

needle.use_own_settings = True
settings = needle.match_settings


# test trained network on a single test sample with image logging
matches = finder.find(needle, haystack)


# cleanup steps
if REMOVE_LOGPATH:
    shutil.rmtree(LOGPATH)
GlobalSettings.image_logging_level = logging.ERROR
GlobalSettings.image_logging_destination = "./imglog"
GlobalSettings.image_logging_step_width = 3
