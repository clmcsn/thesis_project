#!/usr/bin/env python3
#########SETTINGS#########
epochs_num = 90
batch_size = 32
#lr=[0.001,0.0005,0.000025]
import sys
sys.path.append("../")

import os

from common.nnTools import get_all_preds
import models.cifar10.LeNet as LeNet

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim #needed for optimizing the cost function
import torchvision
import torchvision.transforms as transforms
from torch.utils.tensorboard import SummaryWriter

torch.set_grad_enabled(True) #now gradient computation and storing result is needed

network = LeNet.LeNet()

#train the network
train_set = torchvision.datasets.CIFAR10(
    root="../../data/CIFAR10"
    ,train=True
    ,download=True
    ,transform=transforms.Compose([transforms.ToTensor()]))
data_loader = torch.utils.data.DataLoader(
    train_set
    ,batch_size = batch_size)
#setting optimizer
optimizer = optim.Adam(network.parameters(), lr=0.001)
#setting optimizer scheduler
scheduler = optim.lr_scheduler.StepLR(
    optimizer
    ,step_size=30
    ,gamma=0.5)

batch=next(iter(data_loader))
images, labels = batch

#tensorboard init
tb = SummaryWriter()
#grid = torchvision.utils.make_grid(images) #grid for images
#tb.add_image('images',grid)
#tb.add_graph(network,images)

#training
for epoch in range(epochs_num):
    total_loss = 0
    total_correct = 0
    for batch in data_loader:
        images, labels = batch
        optimizer.zero_grad() #clear gradients
        preds = network(images) #forward pass
        loss = F.cross_entropy(preds,labels)
        loss.backward() #calculate gradients
        optimizer.step() #update weights
        total_loss += loss.item()*batch_size
        total_correct += preds.argmax(dim=1).eq(labels).sum().item()
    for param_group in optimizer.param_groups:
        lr=param_group['lr']
    scheduler.step() #lr scheduler
    print("epoch:",epoch,"total_correct:",total_correct,"loss:",total_loss,"lr",lr)
    #saving the epoch stat in tensorboard
    tb.add_scalar('Loss',total_loss, epoch)
    tb.add_scalar('Number Correct',total_correct, epoch)
    tb.add_scalar('Accuracy', total_correct/len(train_set), epoch)

    #recording gradient + loss
    #for name, weight in network.named_parameters():
        #tb.add_histogram(name, weight, epoch)
        #tb.add_histogram('{}.grad'.format(name),weight.grad, epoch)
    #saving network state in case process will crash
    torch.save({
            'epoch': epoch,
            'model_state_dict': network.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': total_loss,
            }, "../models/checkpoints/LeNet_CIFAR10_epoch{}.tar".format(epoch+1))
    if (epoch!=0):
        os.remove("../models/checkpoints/LeNet_CIFAR10_epoch{}.tar".format(epoch))
