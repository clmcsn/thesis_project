#!/usr/bin/env python3

import settings.settings as s

import argpars

parser = argparse.ArgumentParser()
s.network_analyzer_init_parser(parser)
args = parser.parse_args()
s.network_analyzer_check_args(args)

network = s.model_func_dict[args.model](args.dataset)
dataset = s.dataset_func_dict[args.dataset+"_test"]

data_loader= torch.utils.data.DataLoader(
    dataset_d.dbase
    ,shuffle=False
    ,batch_size=args.batch_size)

if args.mode=="single":
    print("Single analysis chosen")
    guided_MaskTable_creator(   network,
                                s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(args.model,args.dataset), 
                                gui=True)