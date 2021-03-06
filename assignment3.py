# -*- coding: utf-8 -*-
"""Assignment3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Lpi0ef65FfqwEinTJKzY3IJfXCXnSYjj
"""

# ------------------------ IMPORTS ------------------------

import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import torch.optim as optim
from __future__ import print_function, division
import os
import pandas as pd
from skimage import io, transform
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import warnings
warnings.filterwarnings("ignore")
plt.ion()
import torchvision.transforms.functional as TF
import torch.nn.functional as F
from PIL import Image
from torchvision.transforms import ToTensor
from torch.autograd import Variable

#------------------------ DATA LOADING CLASSES ----------------------

class AssignmentDataset(Dataset):
    """AssignmentDataset dataset."""

    def __init__(self, root_labels, root_train, transform):
        """
        Args:
            root_labels (string): Directory with all the images for labels.
            root_train (string): Directory with all the images for training.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.root_labels = root_labels
        self.root_train = root_train
        self.transform = transform

    def __len__(self):
        list = os.listdir(self.root_train)
        number_files = len(list)
        print(number_files)
        return number_files

    def __getitem__(self, idx):

        path1 = f"{idx+1}{'_training.tif'}"
        path2 = f"{idx+1}{'_manual1.gif'}"
        img = os.path.join(self.root_train, path1)
        lbl = os.path.join(self.root_labels, path2)
        
        image = Image.open(img)
        sqrWidth = np.ceil(np.sqrt(image.size[0]*image.size[1])).astype(int)
        image = image.resize((sqrWidth, sqrWidth), Image.NEAREST)
        imarray = np.array(image)

        label = Image.open(lbl)
        sqrWidth = np.ceil(np.sqrt(label.size[0]*label.size[1])).astype(int)
        label = label.resize((sqrWidth, sqrWidth), Image.NEAREST)

        [R, G, B] = split_channels(imarray)
        image = transforms.ToTensor()([R, G, B][1])
        label = transforms.ToTensor()(label)

        return image, label  


class AssignmentTestset(Dataset):
    """AssignmentDataset testset."""

    def __init__(self, root_test, transform):
        """
        Args:
            root_test (string): Directory with all the images for testing.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        self.root_test = root_test
        self.transform = transform

    def __len__(self):
        list = os.listdir(self.root_test)
        number_files = len(list)
        return number_files

    def __getitem__(self, idx):

        path_tets = f"{idx+1}{'_test.tif'}"
        img = os.path.join(self.root_test, path_tets)
        
        image = Image.open(img)
        sqrWidth = np.ceil(np.sqrt(image.size[0]*image.size[1])).astype(int)
        image = image.resize((sqrWidth, sqrWidth), Image.NEAREST)
        imarray = np.array(image)

        [R, G, B] = split_channels(imarray)
        image = transforms.ToTensor()([R, G, B][1])
      
        return image

def split_channels(im: np.ndarray):
    assert len(im.shape) == 3 and im.shape[-1] == 3
    return np.squeeze(np.split(im, im.shape[-1], -1), axis=-1)

class ToTensor(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample):
      
        image, label = sample['image'], sample['label']

        image = image.transpose((2, 0, 1))
        label = label.transpose((2, 0, 1))

        #image = ToTensor()(image)
        #label = ToTensor()(label)

        return image, label

# ------------------------ TRAIN DATA ------------------------

trainset = AssignmentDataset(root_train="/content/drive/My Drive/EML_exercise3_data/Images_train/train",
                            root_labels="/content/drive/My Drive/EML_exercise3_data/Labels/labels",
                             transform=None)
                            
trainloader = torch.utils.data.DataLoader(trainset, batch_size=5, 
                                          shuffle=True, num_workers=2)
for i in range(len(trainset)):
    sample = trainset[i]

    print(i, sample[0].shape, sample[1].shape)

    if i == 1:
        print('---------------')
        break

# ------------------------ TEST DATA ------------------------

testset = AssignmentTestset(root_test="/content/drive/My Drive/EML_exercise3_data/Images_test",
                            transform=None)
                                 
testloader = torch.utils.data.DataLoader(testset, batch_size=5, shuffle=False, num_workers=2)

for i in range(len(testset)):
    sample = testset[i]

    print(i, sample[0].shape)

    if i == 1:
        break

# ------------------------ IMAGE METHODS ------------------------

def imshow(img):

    npimg = img.numpy()
    traspose = np.transpose(npimg, (1, 2, 0))
    plt.imshow(traspose)
    plt.show()
    

dataiter = iter(trainloader)
images, labels = dataiter.next()

# ------------------------ SHOW IMAGES TRAIN ------------------------

imshow(torchvision.utils.make_grid(images))
imshow(torchvision.utils.make_grid(labels))


# ------------------------ SHOW IMAGES TEST ------------------------

dataiter_test = iter(testloader)
images_test = dataiter_test.next()
imshow(torchvision.utils.make_grid(images_test))

# ------------------------ USE CPU ------------------------
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# ------------------------ NEURAL NETWORK ------------------------

import torch.nn as nn
import torch.nn.functional as F

# definition of convolutional neural network
class CNN(nn.Module):

  # initialization
  def __init__(self):

        super(CNN, self).__init__()

        self.conv_1 = DoubleConvolution(1, 64, 3) # --> 128
        self.maxPool_1 = MaxPool(2)

        self.conv_2 = DoubleConvolution(64, 128, 3) # --> 256
        self.maxPool_2 = MaxPool(2)

        self.conv_3 = DoubleConvolution(128, 256, 3) # --> 512
        self.maxPool_3 = MaxPool(2)

        self.conv_4 = DoubleConvolution(256, 512, 3) # --> 1024
        self.maxPool_4 = MaxPool(2)

        self.conv_5 = DoubleConvolution(512, 1024, 3)
        self.upConv_5 = UpConvolution(1024, 1024, 2, 2)

        self.conv_6 = DoubleConvolution(1024, 512, 3)
        self.upConv_6 = UpConvolution(512, 512, 2, 2)

        self.conv_7 = DoubleConvolution(512, 256, 3)
        self.upConv_7 = UpConvolution(256, 256, 2, 2)

        self.conv_8 = DoubleConvolution(256, 128, 3)
        self.upConv_8 = UpConvolution(128, 128, 2, 2)

        self.conv_9 = DoubleConvolution(128, 64, 3)
        self.convolution_9 = Convolution(64, 1, 1)

  # Forward fuction
  def forward(self, input):



        result1 = self.conv_1.calculate(input) # --> 128
        result2 = self.maxPool_1.calculate(result1)
        #print('11%')

        result3 = self.conv_2.calculate(result2) # --> 256
        result4 = self.maxPool_2.calculate(result3)
        #print('22%')

        result5 = self.conv_3.calculate(result4) # --> 512
        result6 = self.maxPool_3.calculate(result5)
        #print('33%')

        result7 = self.conv_4.calculate(result6) # --> 1024
        result8 = self.maxPool_4.calculate(result7)
        #print('44%')

        result9 = self.conv_5.calculate(result8)
        result10 = self.upConv_5.calculate(result9)
        #print('55%')

        result10 = self.CopyAndCrop(result7, result10)
        result11 = self.conv_6.calculate(result10) # 1024
        result12 = self.upConv_6.calculate(result11)
        #print('66%')

        result12 = self.CopyAndCrop(result5, result12)
        result13 = self.conv_7.calculate(result12) # 512
        result14 = self.upConv_7.calculate(result13)
        #print('77%')

        result14 = self.CopyAndCrop(result3, result14)
        result15 = self.conv_8.calculate(result14) # 256
        result16 = self.upConv_8.calculate(result15)
        #print('88%')

        result16 = self.CopyAndCrop(result1, result16)
        result17 = self.conv_9.calculate(result16) # 128
        #print('99%')
        result18 = self.convolution_9.calculate(result17)
        #print('100%')
        #print('--------%')

        return result18

  def CopyAndCrop(self, tensor_1, tensor_2):

        extra_dimensions = tensor_2.size()[1] - tensor_1.size()[1]    
        tensor = Variable(tensor_2)
        cropped_tensor = tensor[:,0:extra_dimensions,:,:]

        return torch.cat((cropped_tensor, tensor_1), dim=1)

class MaxPool(nn.Module):

  def __init__(self, dimesion):

      super().__init__()

      self.maxPoll = nn.MaxPool2d(dimesion)

  def calculate(self, input):

        result =  self.maxPoll(input)

        return result
  

class Convolution(nn.Module):

  def __init__(self, number_inputs, number_outputs, kernelSize):

      super().__init__()

      self.conv = nn.Conv2d(number_inputs, number_outputs, 
                            kernel_size=kernelSize)
      self.batch = nn.BatchNorm2d(number_outputs)
      self.relu = nn.ReLU(inplace=True)

  def calculate(self, input):

      result = self.conv(input)
      result = self.batch(result)
      result = self.relu(result)

      return result

class DoubleConvolution(nn.Module):

  def __init__(self, number_inputs, number_outputs, kernelSize):

      super().__init__()

      self.conv = nn.Conv2d(number_inputs, number_outputs, 
                            kernel_size=kernelSize, padding=1, stride=1)
      self.batch = nn.BatchNorm2d(number_outputs)
      self.relu = nn.ReLU(inplace=True)

      self.conv2 = nn.Conv2d(number_outputs, number_outputs, 
                             kernel_size=kernelSize, padding=1, stride=1)
      self.batch2 = nn.BatchNorm2d(number_outputs)
      self.relu2 =  nn.ReLU(inplace=True)

  def calculate(self, input):

      result = self.conv(input)
      result = self.batch(result)
      result = self.relu(result)

      result = self.conv2(result)
      result = self.batch2(result)
      result =  self.relu2(result)

      return result

class UpConvolution(nn.Module):

  def __init__(self, number_inputs, number_outputs, kernelSize, Stride):

      super().__init__()

      self.upConv = nn.ConvTranspose2d(number_inputs, number_outputs, 
                                       kernel_size=kernelSize, stride=2,
                                       output_padding=1)
  def calculate(self, input):

      result =  self.upConv(input)

      return result


net = CNN()

#print(net)

# ------------------------ USE CPU ------------------------
net.to(device)

# ------------------------ OPTIMIZER ------------------------

criterion =  nn.BCEWithLogitsLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

# ------------------------ TRAINING ------------------------

x = []
y = []
loss = 0
for epoch in range(40):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data[0].to(device), data[1].to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        #labels = labels.squeeze(1)
        #labels = labels.long()
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        loss.item()
        print('[%d, %5d] loss: %.3f' %(epoch + 1, i + 1, loss.item()))
        loss = loss.item()
    x.append(epoch+1)
    y.append(loss)
print('Finished Training')

fig = plt.figure(figsize=(18, 3))
ax = fig.add_subplot(111)
ax.scatter(x, y)
ax.plot(x, y)
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
plt.title('Loss over traing epoch', color='white')
plt.xlabel('Epoch', color='white')
plt.ylabel('Loss', color='white')
for a,b in zip(x, y): 
    plt.text(a, b, str(round(b, 3)))
plt.show()

# ------------------------ RESULTS AND TESTING ------------------------
outputs_train = net(images)

plt.figure(figsize=[15, 15])
imshow(torchvision.utils.make_grid(images))
plt.figure(figsize=[15, 15])
imshow(torchvision.utils.make_grid(labels))
with torch.no_grad():
    plt.figure(figsize=[15, 15])
    imshow(torchvision.utils.make_grid(outputs_train))

outputs_test = net(images_test)

from PIL import Image
plt.figure(figsize=[15, 15])
imshow(torchvision.utils.make_grid(images_test))
with torch.no_grad():
    plt.figure(figsize=[15, 15])
    imshow(torchvision.utils.make_grid(outputs_test))
route = '/content/drive/My Drive/EML_exercise3_data/results'
plt.figure(figsize=[15, 15])
imshow(torchvision.utils.make_grid(labels))

#trans = transforms.Compose([transforms.ToPILImage(),])

#for i in range(0,5):
#  img = outputs_test[i]
#  img = trans(img)
  #plt.imshow(img, cmap='gray')
#  img.save(f"{route}/{i+1}_test_result.gif", "gif")