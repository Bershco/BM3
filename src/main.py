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
    parser.add_argument('--n_layers', type=int)
    parser.add_argument('--reg_weight', type=float)
    parser.add_argument('--dropout', type=float)
    parser.add_argument('--mm_weight', type=float)
    parser.add_argument('--seed', type=int)

    config_dict = {
        'gpu_id': 0,
    }

    args, _ = parser.parse_known_args()

    for k in ['n_layers', 'reg_weight', 'dropout', 'mm_weight', 'seed']:
        v = getattr(args, k, None)
        if v is not None:
            config_dict[k] = [v]
            print(f"Override config: {k} = {v}")

    quick_start(model=args.model, dataset=args.dataset, config_dict=config_dict, save_model=True)


