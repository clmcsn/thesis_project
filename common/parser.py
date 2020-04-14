import argparse

import json

conf_var = "../conf_files/conf_var.json"
with open(conf_var) as jv_conf:
    var_conf = json.load(jv_conf)

def _init_parser(parser):
    parser.add_argument("mode",action="store", help="how to use the script") #value to be checked in the application
    parser.add_argument("network",action="store", help="which network you want to use")
    parser.add_argument("dataset",action="store", help="which dataset you want to use")
    parser.add_argument("-bs","--batch_size",action="store",type=int,help="batch size for dataset")

def _check_args(args):
    if not(args.batch_size):
        args.batch_size = 50
    if not (args.network in var_conf["avail_models"]):
        raise ValueError("Specified 'network' is not in the available list")
    if not (args.dataset in var_conf["avail_datasets"]):
        raise ValueError("Specified 'dataset' is not in the available list")          
