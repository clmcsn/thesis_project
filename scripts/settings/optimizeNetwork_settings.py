import torch
import torchvision
import torchvision.transforms as transforms

import os
import sys

sys.path.append("../")

import datetime

TIME_FORMAT = '%Y_%m_%d_%H_%M_%S_%f_%z'
def current_utctime_string(template=TIME_FORMAT):
     return datetime.datetime.now(datetime.timezone.utc).strftime(template)

#lib
distiller_version="../../distiller_mod_v5"
device = 'cuda:1' if torch.cuda.is_available() else 'cpu'

sys.path.append(distiller_version)
import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode

from common.mask_util import MaskType

#file names
maskTimingCharFile="../reports/maskTimingCharact_csaMult_0nsClk.txt"
maskConfig_path = "../models/mask_config/"
checkpoint_path = "../models/checkpoints/"
exchange_fname = "./temp"
res_file = "../reports/gen_Algorithm_Outcome_{}.txt".format(current_utctime_string())

#script
getAccuracy_script_name="./getAccuracy_ON.py"

#network hardware settings
bits=8 #data bits
aw_bits=8
acc_bits=32

quant_mode = LinearQuantMode.ASYMMETRIC_UNSIGNED
mask_mode = MaskType.ARC

#network
network_name = "resnet32"
report_fname = "data_{}_CIFAR10_postTrainMasking_new.txt".format(network_name)
config_fname = "{}.mc".format(network_name)
if (network_name == "vgg11bn"):
    import models.cifar10.vgg_cifar as vgg
    checkpoint_name = "{}_CIFAR10_bestAccuracy_9240.pt".format(network_name)
    maskCharactFile = checkpoint_path + "CIFAR10_bestAccuracy_9240_maskCharact.txt"
    if os.path.exists(maskCharactFile):
        toCharact=False
    else:
        toCharact=True
    unmasked_layers = ["features.0","classifier"]
    network = vgg.vgg11_bn_cifar("")
    network = network.to("cpu") #loaded to cpu because this is a reference, it won't be used for inference and loss of GPU DRAM is avoided 
    network = network.eval() 
    checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location="cpu") #map location for avoiding conflicts
    network.load_state_dict(checkpoint['model_state_dict'])
    network_file_descriptor = "../models/cifar10/net_architectures/vgg11bn_dl.txt"
    ref_correct=9240
elif (network_name == "resnet32"):
    import distiller.models.cifar10 as models
    checkpoint_name = "{}_CIFAR10_bestAccuracy_9358.pt".format(network_name)
    network = models.resnet_cifar.resnet32_cifar()
    network = network.eval()
    checkpoint = torch.load(checkpoint_path + checkpoint_name, map_location="cpu")
    network.load_state_dict(checkpoint['model_state_dict'])
    network_file_descriptor = "../models/cifar10/net_architectures/resnet32_dl.txt"
elif (network_name == "lenet"):
    import models.cifar10.LeNet as LeNet
    checkpoint_name = "{}_CIFAR10_bestAccuracy_7528.pt".format(network_name)
    network = LeNet.LeNet()
    network = network.eval()
    checkpoint = torch.load(checkpoint_path + checkpoint_name, map_location="cpu")
    network.load_state_dict(checkpoint['model_state_dict'])
    network_file_descriptor = "../models/cifar10/net_architectures/lenet_dl.txt"
else:
    errorString = "No checkpoint for {} network. Provide training".format(network_name)
    raise ValueError(network_name)

#load dataset
dataset="CIFAR10"
batch_size = 100
if dataset == "CIFAR10":
    #load test set
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    test_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
        root='../../data/CIFAR10'
        ,train=False  #where data will be located
        ,download=True              #download if is not present offline(run only the first time)
        ,transform=transform_test
    )
    dummy_input = (torch.zeros([1,3,32,32]))
    test_set_size = int(len(test_set))

#genetic algorithm setting
pop_size=50
n_offsprings=5
n_gen=40
max_top1 = 2000
