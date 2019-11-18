#!/usr/bin/env python3

#tensorboard recap is not avelaible

#########SETTINGS#########
epochs_num = 200
batch_size = 50
preTrainedModelPath="../models/checkpoints/LeNet_CIFAR10_epoch200.tar"
preTrainedQuantModelPath="../models/checkpoints/QuantLeNet_CIFAR10_epoch200.tar"

import sys
sys.path.append("../")
sys.path.append("../../distiller")
import os

from common.nnTools import get_all_preds
import models.cifar10.LeNet as LeNet

import torch
import torch.nn as nn
import torch.optim as optim #needed for optimizing the cost function
import torchvision
import torchvision.transforms as transforms
import distiller

def hack_step(model,epoch,batch_num):
    print("Halooo")
    #with("../report/quantWei")


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

if preTrainedModelPath:
    if os.path.isfile(preTrainedModelPath):
        with torch.no_grad():
            #loading network
            preTrainedNetwork = LeNet.LeNet()
            checkpoint = torch.load(preTrainedModelPath)
            preTrainedNetwork.load_state_dict(checkpoint['model_state_dict'])

            #creating data loaders
            test_data_loader= torch.utils.data.DataLoader(
                test_set
                ,batch_size=batch_size)
            
            train_data_loader= torch.utils.data.DataLoader(
                train_set
                ,batch_size=batch_size)

            #forward pass
            train_preds = get_all_preds(preTrainedNetwork, train_data_loader)
            correct_train_predictions=train_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
            train_accuracy=correct_train_predictions/len(train_set)

            test_preds = get_all_preds(preTrainedNetwork, test_data_loader)
            correct_test_predictions=test_preds.argmax(dim=1).eq(torch.LongTensor(test_set.targets)).sum().item()
            test_accuracy=correct_test_predictions/len(test_set)
            #TODO implement a better report
            print(train_accuracy,test_accuracy)
            del preTrainedNetwork

toTrain=True
start_epoch=0
network=LeNet.LeNet()
optimizer = optim.Adam(network.parameters(), lr=0.0005)
quant_net=distiller.quantization.QuantAwareTrainRangeLinearQuantizer(network
                                                                        ,optimizer=optimizer
                                                                        ,bits_activations=8
                                                                        ,bits_weights=8
                                                                        ,bits_bias=8
                                                                        ,overrides=None
                                                                        ,mode=distiller.quantization.LinearQuantMode.SYMMETRIC
                                                                        ,ema_decay=0.999
                                                                        ,per_channel_wts=False
                                                                        ,quantize_inputs=True
                                                                        ,num_bits_inputs=None
)

#setting up the distiller 
dummy_input = (torch.zeros([1,3,32,32]))
quant_net.prepare_model(dummy_input)
quant_net.quantize_params()

if os.path.isfile(preTrainedQuantModelPath):
    print("Checkpoint found!")
    checkpoint = torch.load(preTrainedQuantModelPath)
    quant_net.model.load_state_dict(checkpoint['model_state_dict'])
    

    start_epoch=checkpoint['epoch']+1
    if start_epoch==epochs_num:
        print("Model fully trained!")
        toTrain=False

if toTrain:
    if start_epoch!=0:
        quant_net.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    #setting optimizer scheduler
    scheduler = optim.lr_scheduler.StepLR(
        quant_net.optimizer
        ,step_size=75
        ,gamma=0.5)

    if start_epoch!=0: #if checkpoint load scheduler state
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])


    #setting criterion
    criterion = nn.CrossEntropyLoss()

    #training loop
    for epoch in range(start_epoch,epochs_num):
        total_loss = 0
        total_correct = 0
        for batch_num, batch in enumerate(train_data_loader):
            images, labels = batch
            hack_step(quant_net.moddel,epoch,batch_num,total_loss)
            preds = quant_net.model(images)     #forward pass    
            loss = criterion(preds,labels)      
            quant_net.optimizer.zero_grad()     
            loss.backward()                     #compute gradients
            quant_net.optimizer.step()          #update weights
            quant_net.quantize_params()         #update quantized parameters

            total_loss += loss.item()*batch_size
            total_correct += preds.argmax(dim=1).eq(labels).sum().item()

        for param_group in optimizer.param_groups:
            lr=param_group['lr']
        scheduler.step() #lr scheduler
        
        #print feedback to screen
        print("epoch:",epoch,"total_correct:",total_correct,"loss:",total_loss,"lr",lr)

        #saving network state in case process will crash
        torch.save({
                'epoch': epoch,
                'model_state_dict': quant_net.model.state_dict(),
                'optimizer_state_dict': quant_net.optimizer.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'loss': total_loss,
                }, "../models/checkpoints/QuantLeNet_CIFAR10_epoch{}.tar".format(epoch+1))
        if (epoch!=0):
            os.remove("../models/checkpoints/QuantLeNet_CIFAR10_epoch{}.tar".format(epoch))
#test

#creating data loaders
test_data_loader= torch.utils.data.DataLoader(
    test_set
    ,batch_size=batch_size)

train_data_loader= torch.utils.data.DataLoader(
    train_set
    ,batch_size=batch_size)

#forward pass
train_preds = get_all_preds(quant_net.model, train_data_loader)
correct_train_predictions=train_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
train_accuracy=correct_train_predictions/len(train_set)

test_preds = get_all_preds(quant_net.model, test_data_loader)
correct_test_predictions=test_preds.argmax(dim=1).eq(torch.LongTensor(test_set.targets)).sum().item()
test_accuracy=correct_test_predictions/len(test_set)

print(train_accuracy,test_accuracy)