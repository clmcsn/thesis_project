#!/usr/bin/env python3
#########SETTINGS#########
epochs_num = 120
batch_size = 50
device="cuda"

import sys
sys.path.append("../")

import os


from common.nnTools import get_all_preds
import models.mnist.LeNet as LeNet

#import distiller for models
import sys
sys.path.append("../../distiller_modified")
import distiller
import distiller.models.cifar10 as models

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim #needed for optimizing the cost function
import torchvision
import torchvision.transforms as transforms

model="resnet"
dataset="CIFAR10"
network = models.resnet_cifar.resnet32_cifar()
network.to(device)
#train the network
train_set = torchvision.datasets.CIFAR10(
    root="../../data/CIFAR10"
    ,train=True
    ,download=True
    ,transform=transforms.Compose([transforms.ToTensor()]))
train_data_loader = torch.utils.data.DataLoader(
    train_set
    ,shuffle=True
    ,batch_size = batch_size)

test_set = torchvision.datasets.CIFAR10(                                                            
    root="../../data/CIFAR10"
    ,train=False
    ,download=True
    ,transform=transforms.Compose([transforms.ToTensor()]))
test_data_loader = torch.utils.data.DataLoader(
    test_set
    ,shuffle=False
    ,batch_size = batch_size)

#setting optimizer
optimizer = optim.Adam(network.parameters(), lr=0.0005)
criterion = nn.CrossEntropyLoss()

firstTime=True
#training
for epoch in range(epochs_num):
    network.train()
    for batch_idx, batch in enumerate(train_data_loader):
        images, labels = batch
        images = images.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        preds = network(images)
        loss = criterion(preds, labels)
        correct = preds.argmax(dim=1).eq(labels).sum().item()
        accuracy = correct/len(labels)
        loss.backward()
        optimizer.step()
        if batch_idx % 50 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tAccuracy: {}'.format(
                epoch, batch_idx * len(images), len(train_data_loader.dataset),
                100. * batch_idx / len(train_data_loader), loss.item(), accuracy))
    
    #validating loop
    network.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for images, labels in test_data_loader:
            images = images.to(device)
            labels = labels.to(device)
            preds = network(images)
            test_loss += F.nll_loss(preds, labels, reduction='sum').item()  # sum up batch loss
            correct += preds.argmax(dim=1).eq(labels).sum().item()
    
    test_loss /= len(test_data_loader.dataset)
    if firstTime:
        prev_tloss = test_loss
        best_acc = 100. * correct / len(test_data_loader.dataset)

    print('\nTest set: Epoch: {} Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(epoch,
            test_loss, correct, len(test_data_loader.dataset),
            100. * correct / len(test_data_loader.dataset)))

    torch.save({
            'epoch': epoch,
            'model_state_dict': network.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': test_loss,
            }, "../models/checkpoints/{}_{}_epoch{}.tar".format(model,dataset,epoch+1))
    if (epoch!=0):
        os.remove("../models/checkpoints/{}_{}_epoch{}.tar".format(model,dataset,epoch))
    
    if test_loss<prev_tloss:
        prev_loss = test_loss
        best_acc = 100. * correct / len(test_data_loader.dataset)
        torch.save({
            'epoch': epoch,
            'model_state_dict': network.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': test_loss,
            }, "../models/checkpoints/{}_{}_bestLoss.tar".format(model,dataset))

    print("Best Loss:",test_loss)
