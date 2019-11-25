#!/usr/bin/env python3
#########SETTINGS#########
epochs_num = 5
batch_size = 50
#lr=[0.001,0.0005,0.000025]
device="cpu"

import sys
sys.path.append("../")
sys.path.append("../../distiller")
import os

from common.nnTools import get_all_preds,train,test
import models.cifar10.LeNet as LeNet

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim #needed for optimizing the cost function
import torchvision
import torchvision.transforms as transforms
import distiller
import numpy as np

#fetching train_set
train_set = torchvision.datasets.CIFAR10( #
    root='../../data/CIFAR10'
    ,train=True  
    ,download=True              
    ,transform=transforms.Compose([transforms.ToTensor()])
)

train_data_loader= torch.utils.data.DataLoader(
    train_set
    ,shuffle=True
    ,batch_size=batch_size)

network=LeNet.LeNet()
network.to(device)
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

scheduler = optim.lr_scheduler.StepLR(
        quant_net.optimizer
        ,step_size=15
        ,gamma=0.5)

#setting criterion
criterion = nn.CrossEntropyLoss()
dummy_net=LeNet.LeNet()
#training loop
with open("../reports/hackReport.txt", "w") as log_pointer:
    log_pointer.write("Parameters cointener: params_to_quantize\n")
    log_pointer.write("Container attributes:\n")
    for attributes in dir(quant_net.params_to_quantize):
        log_pointer.write("\t\t\t{}\n".format(attributes))
    log_pointer.write("Parameters :\n")
    for parameter in quant_net.params_to_quantize:
        log_pointer.write("\t\t\t{}\n".format(parameter))
    log_pointer.write("Parameter 0 attributes:\n")
    for attributes in dir(quant_net.params_to_quantize[0]):
        log_pointer.write("\t\t\t{}\n".format(attributes))
    log_pointer.write("Parameters names:\n")
    for parameter in quant_net.params_to_quantize:
        log_pointer.write("\t\t\t{}\n".format(parameter.module_name))
    log_pointer.write("Parameters fp_attr_name s:\n")
    for parameter in quant_net.params_to_quantize:
        log_pointer.write("\t\t\t{}\n".format(parameter.fp_attr_name))
    log_pointer.write("Parameters module s:\n")
    for parameter in quant_net.params_to_quantize:
        log_pointer.write("\t\t\t{}\n".format(parameter.module))
    log_pointer.write("Parameters q_attr_name s:\n")
    for parameter in quant_net.params_to_quantize:
        log_pointer.write("\t\t\t{}\n".format(parameter.q_attr_name))
    log_pointer.write("Module 0 attributes:\n")
    for attributes in dir(quant_net.params_to_quantize[0].module):
        log_pointer.write("\t\t\t{}\n".format(attributes))
    log_pointer.write("New attributes:\n")
    for attributes in dir(quant_net.params_to_quantize[0].module):
        if attributes in dir(dummy_net.conv1):
            pass
        else:
            log_pointer.write("\t\t\t{}\n".format(attributes))
    log_pointer.write("Parameters param_fp type:\n")
    for parameter in quant_net.params_to_quantize:
        log_pointer.write("\t\t\t{}\n".format(type(getattr(parameter.module, parameter.fp_attr_name))))
    
    #IMPORTANTISSIMA SCOPERTA!
    print(id(quant_net.model.conv1))
    print(id(quant_net.params_to_quantize[0].module))
    
    exit()
    for epoch in range(epochs_num):
        quant_net.model.train()
        for batch_idx, batch in enumerate(train_data_loader):
            images, labels = batch
            images = images.to(device)
            labels = labels.to(device)
            quant_net.optimizer.zero_grad()
            preds = quant_net.model(images)
            loss = (preds, labels)
            correct = preds.argmax(dim=1).eq(labels).sum().item()
            accuracy = correct/len(labels)
            loss.backward()
            quant_net.quantize_params()
            quant_net.optimizer.step()
            if (epoch==5 and batch_idx>=45 and batch_idx<=47):
                log_pointer.write("Modules weights for batch{}:\n".format(batch_idx))
                for parameter in quant_net.params_to_quantize:
                    log_pointer.write("\t\t\t{}\n".format(parameter.module.weight.data.numpy()))
                log_pointer.write("Loss:{}\tCorrect:{}\n".format(loss,correct))
                if batch_idx==46:
                    for parameter in quant_net.params_to_quantize:
                        parameter.module.weight=torch.zeros(parameter.module.weight.shape)
        print ("Epoch:{}".format(epoch))
    