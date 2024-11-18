# -*- coding:utf-8 -*-

# %% environment
import chemprop
import descriptastorus
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
# %% function
def hyperopt_train(type, target, split):
    start_time = datetime.now()
    print(f"---------start {target} MPNN hyperopt-------------")
    arguments = [
            '--data_path', f'data/{split}/merge_dataset_train.csv',
            '--dataset_type', 'classification',
            '--num_folds', '5',
            '--num_iters', '30',
            '--show_individual_scores',
            '--config_save_path', f'chemprop_config/{split}/{target}_config_scaffold.json',
            '--epochs', '50',
            '--aggregation', 'norm',
            '--features_generator', 'rdkit_2d_normalized',
            '--no_features_scaling',
            '--gpu', '0',
            '--quiet',
            '--seed', '32',
            '--class_balance',
            '--split_type', 'scaffold_balanced',
        ]
    if type == "single":
        arguments.extend(['--target_columns', f'EC50_{target}'])
    if split != "scaffold":
        args = chemprop.args.HyperoptArgs().parse_args(arguments)
        chemprop.hyperparameter_optimization.hyperopt(args=args)
        print(f"finish {target} MPNN hyperopt, cost time {datetime.now() - start_time}")

    start_time = datetime.now()
    print(f"---------start {target} DMPNN train-------------")
    arguments = [
        '--data_path', f'data/{split}/merge_dataset_train.csv',
        '--separate_test_path', f'data/{split}/merge_dataset_test.csv',
        '--dataset_type', 'classification',
        '--save_dir', f'checkpoints/{split}/checkpoints_{target}_{split}',
        '--epochs', '50',
        '--gpu', '0',
        '--show_individual_scores',
        '--aggregation', 'norm',
        '--features_generator', 'rdkit_2d_normalized',
        '--no_features_scaling',
        '--config_path', f'chemprop_config/{split}/{target}_config_scaffold.json',
        '--ensemble_size', '5',
        '--target_columns', f'EC50_{target}',
        '--quiet',
        '--seed', '32',
        '--class_balance',
        'save_preds'
    ]

    args = chemprop.args.TrainArgs().parse_args(arguments)
    mean_score, std_score = chemprop.train.cross_validate(args=args, train_func=chemprop.train.run_training)
    print(f"{target}, mean_score:{mean_score}")
    print(f"finish {target} MPNN train, cost time {datetime.now() - start_time}")

for split in ["random", "scaffold"]:
    hyperopt_train("mulit", "multi", split)
    for target in ["drer", "dmag", "rsub", "scos"]:
        hyperopt_train("single", target, split)


# %%
def single_task(target):
    start_time = datetime.now()
    print(f"---------start {target} DMPNN hyperopt-------------")
    arguments = [
            '--data_path', 'data/merge_dataset_train.csv',
            '--dataset_type', 'classification',
            '--num_folds', '5',
            '--num_iters', '30',
            '--show_individual_scores',
            '--config_save_path', f'chemprop_config/{target}_config_scaffold.json',
            '--epochs', '50',
            '--aggregation', 'norm',
            '--features_generator', 'rdkit_2d_normalized',
            '--no_features_scaling',
            '--gpu', '0',
            '--target_columns', f'EC50_{target}',
            '--quiet',
            '--seed', '32',
            '--class_balance',
            '--split_type', 'scaffold_balanced',
        ]
    args = chemprop.args.HyperoptArgs().parse_args(arguments)
    chemprop.hyperparameter_optimization.hyperopt(args=args)
    print(f"finish {target} MPNN hyperopt, cost time {datetime.now() - start_time}")

    start_time = datetime.now()
    print(f"---------start {target} MPNN train-------------")
    arguments = [
        '--data_path', 'data/merge_dataset_train.csv',
        '--separate_test_path', 'data/merge_dataset_test.csv',
        '--dataset_type', 'classification',
        '--save_dir', f'checkpoints/checkpoints_{target}_scaffold',
        '--epochs', '50',
        '--gpu', '0',
        '--show_individual_scores',
        '--aggregation', 'norm',
        '--features_generator', 'rdkit_2d_normalized',
        '--no_features_scaling',
        '--config_path', f'chemprop_config/{target}_config_scaffold.json',
        '--ensemble_size', '15',
        '--target_columns', f'EC50_{target}',
        '--quiet',
        '--seed', '32',
        '--class_balance',
    ]

    args = chemprop.args.TrainArgs().parse_args(arguments)
    mean_score, std_score = chemprop.train.cross_validate(args=args, train_func=chemprop.train.run_training)
    print(f"{target}, mean_score:{mean_score}")
    print(f"finish {target} MPNN train, cost time {datetime.now() - start_time}")

# %% multi-task DMPNN
start_time = datetime.now()
print("---------start multi-task MPNN hyperopt-------------")
arguments = [
        '--data_path', 'data/merge_dataset_train.csv',
        '--dataset_type', 'classification',
        '--num_folds', '5',
        '--num_iters', '30',
        '--show_individual_scores',
        '--config_save_path', f'chemprop_config/multi_config.json',
        '--epochs', '50',
        '--aggregation', 'norm',
        '--features_generator', 'rdkit_2d_normalized',
        '--no_features_scaling',
        '--gpu', '0',
        '--quiet',
        '--seed', '32',
        '--class_balance',
        '--split_type', 'scaffold_balanced',
    ]
args = chemprop.args.HyperoptArgs().parse_args(arguments)
chemprop.hyperparameter_optimization.hyperopt(args=args)
print(f"finish multi-task DMPNN hyperopt, cost time {datetime.now() - start_time}")
start_time = datetime.now()

# %%
print("---------start multi-task DMPNN train-------------")
arguments = [
    '--data_path', 'data/merge_dataset_train.csv',
    '--separate_test_path', 'data/merge_dataset_test.csv',
    '--dataset_type', 'classification',
    '--save_dir', 'checkpoints/checkpoints_multi_scaffold_scaffold',
    '--epochs', '50',
    '--gpu', '0',
    '--show_individual_scores',
    '--aggregation', 'norm',
    '--features_generator', 'rdkit_2d_normalized',
    '--no_features_scaling',
    '--config_path', 'chemprop_config/multi_config_scaffold.json',
    '--ensemble_size', '15',
    '--quiet',
    '--seed', '32',
    '--class_balance',
]

args = chemprop.args.TrainArgs().parse_args(arguments)
mean_score, std_score = chemprop.train.cross_validate(args=args, train_func=chemprop.train.run_training)
print(f"multi-task, mean_score:{mean_score}")
print(f"finish multi-task MPNN train, cost time {datetime.now() - start_time}")

# %% single task
print("---------start single-task DMPNN train-------------")
targets = ["drer", "dmag", "rsub", "scos"]
for target in targets:
    single_task(target)


# %% Train all my multi-task DMPNN
print("---------start multi-task DMPNN hyperopt-------------")
arguments = [
        '--data_path', 'data/merge_dataset.csv',
        '--dataset_type', 'classification',
        '--num_folds', '5',
        '--num_iters', '20',
        '--show_individual_scores',
        '--config_save_path', f'chemprop_config/multi_config_all.json',
        '--epochs', '30',
        '--aggregation', 'norm',
        '--features_generator', 'rdkit_2d_normalized',
        '--no_features_scaling',
        '--gpu', '0',
        '--quiet',
        '--seed', '3407',
        '--class_balance',
        '--split_type', 'scaffold_balanced',
    ]
args = chemprop.args.HyperoptArgs().parse_args(arguments)
start_time = datetime.now()
chemprop.hyperparameter_optimization.hyperopt(args=args)
print(f"finish multi-task DMPNN hyperopt, cost time {datetime.now() - start_time}")
start_time = datetime.now()


print("---------start multi-task DMPNN train-------------")
arguments = [
    '--data_path', 'data/merge_dataset.csv',
    '--dataset_type', 'classification',
    '--save_dir', 'checkpoints/checkpoints_multi_all',
    '--epochs', '30',
    '--gpu', '0',
    '--show_individual_scores',
    '--aggregation', 'norm',
    '--features_generator', 'rdkit_2d_normalized',
    '--no_features_scaling',
    '--config_path', 'chemprop_config/multi_config_all.json',
    '--ensemble_size', '5',
    '--quiet',
    '--seed', '3407',
    '--class_balance',
    '--num_folds', '5',
    '--split_sizes', '0.8', '0.2', '0',
]

args = chemprop.args.TrainArgs().parse_args(arguments)
chemprop.train.cross_validate(args=args, train_func=chemprop.train.run_training)
print(f"finish multi-task MPNN train, cost time {datetime.now() - start_time}")


# %% predict
predict_arguments = [
    '--test_path', f'lotus/lotus_smiles_with_cas.csv',
    '--preds_path', f'lotus/smiles_with_cas_preds.csv',
    '--checkpoint_dir', 'checkpoints/checkpoints_multi_all',
    '--features_generator', 'rdkit_2d_normalized',
    '--no_features_scaling',
    '--gpu', '0',
    '--num_workers', '0',
    '--smiles_columns', 'smiles'
]
args = chemprop.args.PredictArgs().parse_args(predict_arguments)
preds = chemprop.train.make_predictions(args=args)
