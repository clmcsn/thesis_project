#!/usr/bin/env python3

#tensorboard recap is not avelaible

#########SETTINGS#########
epochs_num = 350
batch_size = 50

device="cpu"

import sys
sys.path.append("../")
sys.path.append("../../distiller")
import os

from common.nnTools import get_all_preds,train,test

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim #needed for optimizing the cost function
import torchvision
import torchvision.transforms as transforms
import distiller
import distiller.models.cifar10 as models

from common.mask_util import MaskTable,MaskType

#fetching train_set
train_set = torchvision.datasets.CIFAR10( #
    root='../../data/CIFAR10'
    ,train=True  
    ,download=True              
    ,transform=transforms.Compose([transforms.ToTensor()])
)

#fetching test_set
test_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
    root='../../data/CIFAR10'
    ,train=False
    ,download=True
    ,transform=transforms.Compose([transforms.ToTensor()])
)

#creating data loaders
test_data_loader= torch.utils.data.DataLoader(
    test_set
    ,shuffle=False
    ,batch_size=batch_size)

train_data_loader= torch.utils.data.DataLoader(
    train_set
    ,shuffle=True
    ,batch_size=batch_size)


toTrain=True
start_epoch=0
model="resnet32"
dataset="CIFAR10"
network=models.resnet_cifar.resnet32_cifar()
network.to(device)
optimizer = optim.SGD(network.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4)
mask_table=MaskTable(distiller.quantization.LinearQuantMode.SYMMETRIC, MaskType.MOD_ROUND_UP, [2,1], True, network)
quant_net=distiller.quantization.QuantAwareTrainRangeLinearQuantizer(network
                                                                        ,optimizer=optimizer
                                                                        ,bits_activations=8
                                                                        ,bits_weights=8
                                                                        ,bits_bias=8
                                                                        ,overrides=None
                                                                        ,mode=distiller.quantization.LinearQuantMode.SYMMETRIC
                                                                        ,mask_table=mask_table
                                                                        ,ema_decay=0.999
                                                                        ,per_channel_wts=False
                                                                        ,quantize_inputs=True
                                                                        ,num_bits_inputs=None
)

scheduler = optim.lr_scheduler.StepLR(quant_net.optimizer, 120, gamma=0.1, last_epoch=-1)

#setting up the distiller 
dummy_input = (torch.zeros([1,3,32,32]))
quant_net.prepare_model(dummy_input)
quant_net.quantize_params()
quant_net.model.to(device)


if toTrain:
    if start_epoch!=0:
        quant_net.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    """#setting optimizer scheduler
    scheduler = optim.lr_scheduler.StepLR(
        quant_net.optimizer
        ,step_size=30
        ,gamma=0.5)

    if start_epoch!=0: #if checkpoint load scheduler state
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])"""


    #setting criterion
    criterion = nn.CrossEntropyLoss()

    #training loop
    for epoch in range(start_epoch,epochs_num):
        quant_net.model.train()
        for batch_idx, batch in enumerate(train_data_loader):
            images, labels = batch
            images = images.to(device)
            labels = labels.to(device)
            quant_net.optimizer.zero_grad()
            preds = quant_net.model(images)
            loss = criterion(preds, labels)
            correct = preds.argmax(dim=1).eq(labels).sum().item()
            accuracy = correct/len(labels)
            loss.backward()
            quant_net.optimizer.step()
            quant_net.quantize_params()
            if batch_idx % 50 == 0:
                print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tAccuracy: {}'.format(
                    epoch, batch_idx * len(images), len(train_data_loader.dataset),
                    100. * batch_idx / len(train_data_loader), loss.item(), accuracy))
    
        #validating loop
        quant_net.model.eval()
        test_loss = 0
        correct = 0
        with torch.no_grad():
            for images, labels in test_data_loader:
                images = images.to(device)
                labels = labels.to(device)
                preds = quant_net.model(images)
                test_loss += F.nll_loss(preds, labels, reduction='sum').item()  # sum up batch loss
                correct += preds.argmax(dim=1).eq(labels).sum().item()
        
        test_loss /= len(test_data_loader.dataset)
        scheduler.step()
        print('\nTest set: Epoch: {} Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(epoch,
            test_loss, correct, len(test_data_loader.dataset),
            100. * correct / len(test_data_loader.dataset)))

        for param_group in optimizer.param_groups:
            lr=param_group['lr']
        #scheduler.step() #lr scheduler
        
        #print feedback to screen
        #print("epoch:",epoch,"total_correct:",total_correct,"loss:",total_loss,"lr",lr)

        #saving network state in case process will crash
        torch.save({
                'epoch': epoch,
                'model_state_dict': quant_net.model.state_dict(),
                'optimizer_state_dict': quant_net.optimizer.state_dict(),
               # 'scheduler_state_dict': scheduler.state_dict(),
                }, "../models/checkpoints/{}_{}_epoch{}.tar".format(model,dataset,epoch+1))
        if (epoch!=0):
            os.remove("../models/checkpoints/{}_{}_epoch{}.tar".format(model,dataset,epoch))
        
        if firstTime:
            prev_tcorr = correct
            best_acc = 100. * correct / len(test_data_loader.dataset)
            firstTime = False

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