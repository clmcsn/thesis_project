#!/usr/bin/env python3

#########SETTINGS#########
epochs_num = 5
batch_size = 32
#lr=[0.001,0.0005,0.000025]
import sys
sys.path.append("../")
sys.path.append("../../distiller")
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
import distiller
from copy import deepcopy

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
criterion = nn.CrossEntropyLoss()
#wrapp around quantizer
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
                                                                        ,num_bits_inputs=None)
quant_net.model.train()
dummy_input = (torch.zeros([1,3,32,32]))
quant_net.prepare_model(dummy_input)
quant_net.quantize_params()
with open("../reports/quant_Weights.txt","w") as weight_file:
    weight_file.write("FP WEIGHT 1 LAYER:\n{}\n".format(quant_net.params_to_quantize[0].module.float_weight[0]))
    weight_file.write("QUANT WEIGHT 1 LAYER:\n{}\n".format(quant_net.params_to_quantize[0].module.weight[0]))
    weight_file.write("WEIGHT FROM MODULE 1 LAYER:\n{}\n".format(list(quant_net.model.parameters())[0][0]))
    for epoch in range(epochs_num):
        total_loss = 0
        total_correct = 0
        for batch in data_loader:
            images, labels = batch
            preds = quant_net.model(images) #forward pass
            loss = criterion(preds,labels)
            quant_net.optimizer.zero_grad() #clear gradients
            loss.backward() #calculate gradients
            quant_net.optimizer.step() #update weights
            quant_net.quantize_params()
            #iterate through all weights(layer+channel)
            total_loss += loss.item()*batch_size
            total_correct += preds.argmax(dim=1).eq(labels).sum().item()
        for param_group in optimizer.param_groups:
            lr=param_group['lr']
        scheduler.step() #lr scheduler
        print("epoch:",epoch,"total_correct:",total_correct,"loss:",total_loss,"lr",lr)
        weight_file.write("\nEPOCH:{}".format(epoch))
        weight_file.write("FP WEIGHT 1 LAYER:\n{}\n".format(quant_net.params_to_quantize[0].module.float_weight[0]))
        weight_file.write("QUANT WEIGHT 1 LAYER:\n{}\n".format(quant_net.params_to_quantize[0].module.weight[0]))
        weight_file.write("WEIGHT FROM MODULE 1 LAYER:\n{}\n".format(list(quant_net.model.parameters())[0][0]))
        weight_file.write("\n")