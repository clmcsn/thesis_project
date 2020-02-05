#!/usr/bin/env python3

import sys
sys.path.append("../")
sys.path.append("../../distiller_modified")

import torch
import distiller
import torchvision
import torchvision.transforms as transforms
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
from copy import deepcopy
from common.nnTools import get_all_preds
import models.cifar10.LeNet as LeNet
from common.mask_util import MaskType
import distiller.utils
from distiller.data_loggers import collect_quant_stats


network = LeNet.LeNet()
checkpoint = torch.load('../models/checkpoints/LeNet_CIFAR10_epoch100.tar', map_location='cpu')
network.load_state_dict(checkpoint['model_state_dict'])


train_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
    root='../../data/CIFAR10'
    ,train=False  #where data will be located
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
#gives the number of correct predictions
preds_correct = train_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
print('total correct:', preds_correct)
print('accuracy:', preds_correct/len(train_set),'len:',len(train_set))
print
#distiller.utils.assign_layer_fq_names(checkpoint)
#collector = QuantCalibrationStatsCollector(checkpoint)
#stats_file = './acts_quantization_stats.yaml'

quantizer = PostTrainLinearQuantizer(deepcopy(network), bits_activations=8, bits_parameters=8, bits_accum=32,
                 mode=LinearQuantMode.ASYMMETRIC_SIGNED,mask=MaskType.MINIMUM_DISTANCE, maskList=[1], correctRange=True,
                 scale_approx_mult_bits=8)
dummy_input = (torch.zeros([1,3,32,32]))
quantizer.prepare_model(dummy_input)
quantizer.model.eval()
train_preds = get_all_preds(quantizer.model, data_loader)
torch.save({
        'epoch': checkpoint['epoch'],
        'model_state_dict': network.state_dict()
        }, "../models/checkpoints/LeNet_postTrainQuant_CIFAR10.tar")
#gives the number of correct predictions
preds_correct = train_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
#print(train_preds.argmax(dim=1))
print('total correct:', preds_correct)
print('accuracy:', preds_correct/len(train_set),'len:',len(train_set))
#stats_before_prepare = deepcopy(quantizer.model_activation_stats)
#dummy_input = (torch.zeros(1,1).to(dtype=torch.long), checkpoint.init_hidden(1))
#quantizer.prepare_model(dummy_input)
#print(quantizer.model)
#print(network.state_dict())
#print(quantizer.model.state_dict())
