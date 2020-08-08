#!/usr/bin/env python3

import settings.settings as s
from common.mask_util import MaskTable, guided_MaskTable_creator
from common.hw_lib import printer_2s

import torch
import argparse

parser = argparse.ArgumentParser()
s.network_analyzer_init_parser(parser)
args = parser.parse_args()
s.network_analyzer_check_args(args)

network = s.model_func_dict[args.network](args.dataset)
dataset = s.dataset_func_dict[args.dataset+"_test"]()

data_loader= torch.utils.data.DataLoader(
    dataset.dbase
    ,shuffle=False
    ,batch_size=args.batch_size)

if args.mode=="single":
    print("Single analysis chosen.")
    if args.auto_mask:
        guided_MaskTable_creator(   network,
                                s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset),
                                std_mask=args.mask, 
                                gui=False)
    else:
        guided_MaskTable_creator(   network,
                                    s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset),
                                    std_mask=args.mask, 
                                    gui=True)
    mask_table = MaskTable( int(s.var_conf["bits"]),
                            s.quant_mode_dic[s.var_conf["quant_mode"]],
                            s.mask_mode_dic[s.var_conf["mask_mode"]], 
                            network, 
                            mask=[] , 
                            correctRange=False, 
                            mask_file=s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset))
    accuracy = s.evaluate_network(  network,
                                    mask_table,
                                    dataset,
                                    data_loader,
                                    device=s.var_conf["server_dev"])
    print("Accuracy:{}".format(accuracy))
elif args.mode=="quantization":
    with open(s.path_conf["report"]+s.path_conf["unif_quant_acc_file"].format(model=args.network,
                                                                              dataset=args.dataset,
                                                                              version=s.current_utctime_string()),"w") as out_pointer:
        for qm in s.var_conf["quant_mode_list"]:
            quant_mode = s.quant_mode_dic[qm]
            for b in range(int(s.var_conf["bits"]), int(s.var_conf["lowest_qbits"])-1,-1):
                mask_table = MaskTable( b,
                                        quant_mode,
                                        s.mask_mode_dic[s.var_conf["mask_mode"]], 
                                        network, 
                                        mask=[] , 
                                        correctRange=False, 
                                        mask_file=s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset))
                accuracy = s.evaluate_network(  network,
                                    mask_table,
                                    dataset,
                                    data_loader,
                                    device=s.var_conf["server_dev"])
                del mask_table
                out_pointer.write(s.strings["q_rep_string"].format(quant_mode,b,accuracy))
elif args.mode=="mask":
    with open(s.path_conf["report"]+s.path_conf["unif_mask_acc_file"].format(model=args.network,
                                                                             dataset=args.dataset,
                                                                             version=s.current_utctime_string()),"w") as out_pointer:
        for qm in s.var_conf["quant_mode_list"]:
            quant_mode = s.quant_mode_dic[qm]
            for mm in s.var_conf["mask_mode_list"]:
                mask_mode = s.mask_mode_dic[mm]
                for i in range(1,int(s.var_conf["highest_mask"])):
                    mask = printer_2s(i,int(s.var_conf["bits"]))
                    #baseline accuracy
                    guided_MaskTable_creator(   network,
                                                s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset),
                                                mask,
                                                correctRange=False, 
                                                gui=False)
                    mask_table = MaskTable( int(s.var_conf["bits"]),
                                            quant_mode, 
                                            mask_mode, 
                                            network, 
                                            mask=None , 
                                            correctRange=None, 
                                            mask_file=s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset))
                    b_accuracy = s.evaluate_network(  network,
                                                    mask_table,
                                                    dataset,
                                                    data_loader,
                                                    device=s.var_conf["server_dev"])
                    bc_accuracy = s.evaluate_network(  network,
                                                    mask_table,
                                                    dataset,
                                                    data_loader,
                                                    device=s.var_conf["server_dev"],
                                                    compensate=True)
                    del mask_table
                    #range corrected accuracy
                    guided_MaskTable_creator(   network,
                                                s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset),
                                                mask,
                                                correctRange=True, 
                                                gui=False)
                    mask_table = MaskTable( int(s.var_conf["bits"]),
                                            quant_mode, 
                                            mask_mode, 
                                            network, 
                                            mask=None , 
                                            correctRange=None, 
                                            mask_file=s.path_conf["mask_config"]+s.path_conf["mask_config_file"].format(model=args.network,dataset=args.dataset))
                    c_accuracy = s.evaluate_network(  network,
                                                    mask_table,
                                                    dataset,
                                                    data_loader,
                                                    device=s.var_conf["server_dev"])
                    cc_accuracy = s.evaluate_network(  network,
                                                    mask_table,
                                                    dataset,
                                                    data_loader,
                                                    device=s.var_conf["server_dev"],
                                                    compensate=True)
                    del mask_table
                    out_pointer.write(s.strings["m_rep_string"].format( quant_mode,
                                                                        s.var_conf["bits"],
                                                                        mask_mode,
                                                                        mask,
                                                                        b_accuracy,
                                                                        bc_accuracy,
                                                                        c_accuracy,
                                                                        cc_accuracy))
                    
