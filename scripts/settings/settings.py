conf_path = "../conf_files/conf_path.json"
conf_var = "../conf_files/conf_var.json"
conf_str = "../conf_files/strings.json"

import json
with open(conf_path) as jp_conf:
    path_conf = json.load(jp_conf)
with open(conf_var) as jv_conf:
    var_conf = json.load(jv_conf)
with open(conf_str) as js_conf:
    strings = json.load(js_conf)

import sys
for p in path_conf["appends"]:
    sys.path.append(p)

from copy import deepcopy

import torch
from quantization import LinearQuantMode,PostTrainLinearQuantizer
from common.mask_util import MaskType, compensateNetwork, MaskTable
from common.nnTools import get_all_preds
from collections import namedtuple

import datetime
TIME_FORMAT = '%Y_%m_%d_%H_%M_%S_%f_%z'
def current_utctime_string(template=TIME_FORMAT):
     return datetime.datetime.now(datetime.timezone.utc).strftime(template)

quant_mode_dic = {  "LinearQuantMode.ASYMMETRIC_UNSIGNED" : LinearQuantMode.ASYMMETRIC_UNSIGNED,
                    "LinearQuantMode.ASYMMETRIC_SIGNED" : LinearQuantMode.ASYMMETRIC_SIGNED,
                    "LinearQuantMode.SYMMETRIC" : LinearQuantMode.SYMMETRIC}

mask_mode_dic = {   "MaskType.ARC" : MaskType.ARC,
                    "MaskType.SIMPLE_MASK" : MaskType.SIMPLE_MASK}

#network generation class
def vgg11bn_gen(dataset):
    import models.cifar10.vgg_cifar as vgg
    network = vgg.vgg11_bn_cifar("")
    network = network.eval()
    checkpoint = torch.load(path_conf["checkpoint"]+path_conf["ba_checkpoint_file"].format( model=var_conf["vgg11bn_name"],
                                                                                            dataset=dataset,
                                                                                            accuracy=var_conf["vgg11bn_{}_acc".format(dataset)]))
    network.load_state_dict(checkpoint['model_state_dict'])
    return network

def resnet32_gen(dataset):
    import distiller.models.cifar10 as models
    network = models.resnet_cifar.resnet32_cifar()
    network = network.eval()
    checkpoint = torch.load(path_conf["checkpoint"]+path_conf["ba_checkpoint_file"].format( model=var_conf["resnet32_name"],
                                                                                            dataset=dataset,
                                                                                            accuracy=var_conf["resnet32_{}_acc".format(dataset)]))
    network.load_state_dict(checkpoint['model_state_dict'])
    return network

def lenet_gen(dataset):
    import models.cifar10.LeNet as LeNet
    network = LeNet.LeNet()
    network = network.eval()
    checkpoint = torch.load(path_conf["checkpoint"]+path_conf["ba_checkpoint_file"].format( model=var_conf["lenet_name"],
                                                                                            dataset=dataset,
                                                                                            accuracy=var_conf["lenet_{}_acc".format(dataset)]))
    network.load_state_dict(checkpoint['model_state_dict'])
    return network

model_func_dict = { 'vgg11bn'   : vgg11bn_gen,
                    'resnet32'  : resnet32_gen,
                    'lenet'     : lenet_gen}

DatasetAttributes = namedtuple("DatasetAttributes",['dbase','dummy_input'])

def CIFAR10_test_gen():
    import torchvision
    import torchvision.transforms as transforms
    
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    test_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
        root=path_conf["datasets"].format(dataset="CIFAR10")
        ,train=False  #where data will be located
        ,download=True              #download if is not present offline(run only the first time)
        ,transform=transform_test
    )
    dummy_input = (torch.zeros([1,3,32,32]))

    r_dic=DatasetAttributes(dbase=test_set,dummy_input=dummy_input)
    
    return r_dic

dataset_func_dict = {'CIFAR10_test' : CIFAR10_test_gen}

from common.parser import _init_parser, _check_args

def network_analyzer_init_parser(parser):
    _init_parser(parser)
    parser.add_argument("-mcf", "--mask_conf_file", action="store", help="file name of the configuration mask file")

def network_analyzer_check_args(args):
    _check_args(args)
    if not (args.mode in var_conf["avail_modes"]):
        raise ValueError("Specified 'mode' is not in the available list")
    if args.mode=="single":
        if not (args.mask_conf_file):
            raise ValueError("Please specify a file for the network mask configuration")

def evaluate_network(network,mask_table,dataset,data_loader,device='cpu',compensate=False):
    quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=int(var_conf["aw_bits"]), bits_parameters=mask_table.w_bits, bits_accum=int(var_conf["acc_bits"]),
                                            mode=mask_table.quant_mode, mask_table=mask_table,
                                            scale_approx_mult_bits=int(var_conf["bits"]))
    quantizer.model.to("cpu")
    quantizer.prepare_model(dataset.dummy_input)
    quantizer.model.eval()
    if compensate:
        ref_mask_table = MaskTable(int(var_conf["bits"]),mask_table.quant_mode, MaskType.SIMPLE_MASK, network, [] , False)
        ref = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=int(var_conf["aw_bits"]), bits_parameters=mask_table.w_bits, bits_accum=int(var_conf["acc_bits"]),
                                            mode=mask_table.quant_mode, mask_table=ref_mask_table,
                                            scale_approx_mult_bits=int(var_conf["bits"]))
        ref.model.to("cpu")
        ref.prepare_model(dataset.dummy_input)
        quantizer.model.to("cpu")
        ref.model.eval()
        compensateNetwork( ref.model,
                        quantizer.model,
                        dataset.dbase,
                        conf_path,
                        batch_size=500,
                        device="cpu")
    quantizer.model.to(device)
    test_preds = get_all_preds(quantizer.model, data_loader,device=device)
    preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(dataset.dbase.targets).to(device)).sum().item()
    del quantizer
    return preds_correct
