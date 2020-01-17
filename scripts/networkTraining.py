#!/usr/bin/env python3
#########SETTINGS#########
epochs_num = 300
batch_size = 100

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

device = 'cuda:1' if torch.cuda.is_available() else 'cpu'
model="resnet32"
dataset="CIFAR10"
network = models.resnet_cifar.resnet32_cifar()
network.to(device)

transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

train_set = torchvision.datasets.CIFAR10(
    root="../../data/CIFAR10"
    ,train=True
    ,download=True
    ,transform=transform_train)
train_data_loader = torch.utils.data.DataLoader(
    train_set
    ,shuffle=True
    ,batch_size = batch_size
    ,num_workers=2)

test_set = torchvision.datasets.CIFAR10(                                                            
    root="../../data/CIFAR10"
    ,train=False
    ,download=True
    ,transform=transform_test)
test_data_loader = torch.utils.data.DataLoader(
    test_set
    ,shuffle=False
    ,batch_size = batch_size
    ,num_workers=2)

#setting optimizer
#optimizer = optim.Adam(network.parameters(), lr=0.0001, weight_decay=0.0005)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(network.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4)
scheduler = optim.lr_scheduler.StepLR(optimizer, 120, gamma=0.1, last_epoch=-1)
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
    
    scheduler.step()
    test_loss /= len(test_data_loader.dataset)
    
    if firstTime:
        prev_tcorr = correct
        best_acc = 100. * correct / len(test_data_loader.dataset)
        firstTime = False

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
    
    if correct > prev_tcorr:
        prev_tcorr = correct
        best_acc = 100. * correct / len(test_data_loader.dataset)
        torch.save({
            'epoch': epoch,
            'model_state_dict': network.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': test_loss,
            }, "../models/checkpoints/{}_{}_bestAccuracy.tar".format(model,dataset))

    print("Best acc:{}\n".format(best_acc))
