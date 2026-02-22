# coding: utf-8
# @email: enoche.chow@gmail.com

"""
Main entry
# UPDATED: 2022-Feb-15
##########################
"""

import os
import argparse
from utils.quick_start import quick_start
os.environ['NUMEXPR_MAX_THREADS'] = '48'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', '-m', type=str, default='BM3', help='name of models')
    parser.add_argument('--dataset', '-d', type=str, default='baby', help='name of datasets')
    parser.add_argument('--n_layers', type=int, default=2, help='the number of layers in the model, default is 2')
    parser.add_argument('--reg_weight', type=float, default=0.01, help='the weight of the regularization term, default is 0.01')
    parser.add_argument('--dropout', type=float, default=0.5, help='the dropout rate, default is 0.5')
    parser.add_argument('--mm_weight', type=float, default=1.0, help='the weight of the MM loss, default is 1.0')
    parser.add_argument('--seed', type=int, default=999, help='random seed for reproducibility')
    parser.add_argument('--load_model_path', type=str, default=None, help='the path of the model to be loaded, default is None, which means not loading any model')
    parser.add_argument('--inference_only', action='store_true', help='whether only run inference, default is False')
    parser.add_argument('--retrieve_mgod', action='store_true', help='whether retrieve modality gate output distribution, default is False')


    config_dict = {
        'gpu_id': 0,
    }

    args, _ = parser.parse_known_args()

    for k in ['n_layers', 'reg_weight', 'dropout', 'mm_weight', 'seed']:
        v = getattr(args, k, None)
        if v is not None:
            config_dict[k] = [v]
            print(f"Override config: {k} = {v}")

    if args.inference_only:
        config_dict['inference_only'] = True
        print("Inference only mode enabled.")
    if args.load_model_path is not None:
        config_dict['load_model'] = True
        config_dict['load_model_path'] = args.load_model_path
        print(f"Model loading enabled. Path: {args.load_model_path}")
    if args.retrieve_mgod:
        config_dict['retrieve_mgod'] = True
        print("Retrieving modality gate output distribution enabled.")

    quick_start(model=args.model, dataset=args.dataset, config_dict=config_dict, save_model=True)


