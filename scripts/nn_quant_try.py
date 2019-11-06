#!/usr/bin/env python3

#lr=[0.001,0.0005,0.000025]
import sys
sys.path.append("../")
sys.path.append("../../distiller")

import torch
import distiller
import torchvision
import torchvision.transforms as transforms
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
from copy import deepcopy
from common.nnTools import get_all_preds
import models.cifar10.LeNet as LeNet

network = LeNet.LeNet()
checkpoint = torch.load('../models/checkpoints/LeNet_CIFAR10_epoch90.tar')
network.load_state_dict(checkpoint['model_state_dict'])

train_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
    root='../../data/CIFAR10'
    ,train=True  #where data will be located
    ,download=True              #download if is not present offline(run only the first time)
    ,transform=transforms.Compose([ #transformation of data to tensor
        transforms.ToTensor()
    ])
)

batch_size=1000
data_loader= torch.utils.data.DataLoader(
    train_set
    ,batch_size=batch_size)
train_preds = get_all_preds(network, data_loader)
preds_correct = train_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
#print(type(preds_correct))
#print(type(torch.Tensor(train_set.targets)))
#exit()
print('total correct:', preds_correct)
print('accuracy:', preds_correct/len(train_set),'len:',len(train_set))
