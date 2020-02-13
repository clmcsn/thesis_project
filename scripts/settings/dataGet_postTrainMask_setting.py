import torch
import torchvision
import torchvision.transforms as transforms
import sys
sys.path.append("../")
from common.mask_util import MaskType

#pats
checkpoint_path = "../models/checkpoints/"
maskConfig_path = "../models/mask_config/"
report_path = "../reports/"

#lib
distiller_version="../../distiller_mod_v5"
device = 'cuda:1' if torch.cuda.is_available() else 'cpu'

sys.path.append(distiller_version)
import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode

#report strings
rep_file = "../reports/data_vgg11bn_CIFAR10_postTrainMask_v2.txt"
rep_string = "QuantMode: {}\t MaskMode: {}\t Mask: {}\n"
acc_string = "\t{} accuracy = \t{}\n"

#algorithm to be analyzed
quant_mode_list = [LinearQuantMode.ASYMMETRIC_UNSIGNED]
#mask_mode_list = [MaskType.SIMPLE_MASK,MaskType.ROUND_DOWN,MaskType.ROUND_UP,MaskType.MOD_ROUND_UP,MaskType.MINIMUM_DISTANCE, MaskType.MD]
mask_mode_list = [MaskType.MD_FAST]

#report masks to be analyzed
stop_string = 24

#target hardware
bits=8 #data bits
aw_bits=8
acc_bits=32

#network
network_name = "vgg11bn"
report_fname = "data_{}_CIFAR10_postTrainMasking_new.txt".format(network_name)
config_fname = "{}.mc".format(network_name)
if (network_name == "vgg11bn"):
    import models.cifar10.vgg_cifar as vgg
    checkpoint_name = "{}_CIFAR10_bestAccuracy_9240.pt".format(network_name)
    unmasked_layers = ["features.0","classifier"]
    network = vgg.vgg11_bn_cifar("./data/ref_model")
elif (network_name == "resnet32"):
    import distiller.models.cifar10 as models
    checkpoint_name = "{}_CIFAR10_bestAccuracy_9358.pt".format(network_name)
    unmasked_layers = ["conv1","fc"]
    network = models.resnet_cifar.resnet32_cifar()
else:
    raise ValueError("No checkpoint for {} network. Provide training".format(network_name))

#load dataset
dataset="CIFAR10"
batch_size = 100
if dataset == "CIFAR10":
    #load test set
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    train_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
        root='../../data/CIFAR10'
        ,train=False  #where data will be located
        ,download=True              #download if is not present offline(run only the first time)
        ,transform=transform_test
    )
    dummy_input = (torch.zeros([1,3,32,32]))
