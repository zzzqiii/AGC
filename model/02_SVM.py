# -*- coding:utf-8 -*-

# %% environment
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import chemprop
from sklearn.metrics import roc_auc_score,roc_curve, auc, average_precision_score, accuracy_score, precision_score, recall_score, f1_score
from bayes_opt import BayesianOptimization
from bayes_opt.util import Colours
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from sklearn.ensemble import RandomForestClassifier
from skopt import BayesSearchCV
from xgboost import XGBClassifier
from sklearn.utils import resample
import joblib


# %% function
def get_target_dataset(target, type, split):
    all_mols = pd.read_csv(f"data/merge_{split}_{type}.csv", usecols=["smiles", f"EC50_{target}"])
    target_mols = all_mols[~np.isnan(all_mols[f'EC50_{target}'])]
    features = target_mols["smiles"].apply(chemprop.features.features_generators.rdkit_2d_normalized_features_generator)
    features = np.array(features.apply(pd.Series))
    targets = np.array(target_mols[f'EC50_{target}'])
    return features, targets

# %%
def printModelResultWithConfidence(model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    print(model)
    prob_train = model.predict_proba(X_train)
    print("roc score (Train): %f" % roc_auc_score(y_train, prob_train[:, 1]))
    binary_predictions = model.predict(X_test)
    prob_test = model.predict_proba(X_test)
    test_auc = roc_auc_score(y_test, prob_test[:, 1])

    prauc = average_precision_score(y_test, prob_test[:, 1])
    accuracy = accuracy_score(y_test, binary_predictions)
    precision = precision_score(y_test, binary_predictions)
    recall = recall_score(y_test, binary_predictions)
    f1score = f1_score(y_test, binary_predictions)

    print("roc score (Test): %f" % test_auc)

    n_bootstrap = 1000
    auc_scores = []
    for i in range(n_bootstrap):
        y_test_sample, y_pred_sample = resample(y_test, prob_test[:, 1])
        test_auc_bootstrap = roc_auc_score(y_test_sample, y_pred_sample)
        auc_scores.append(test_auc_bootstrap)
    average_auc = np.mean(auc_scores)
    std_auc = np.std(auc_scores)

    print(average_auc, std_auc)
    return [average_auc, std_auc, test_auc, prauc, accuracy, precision, recall, f1score]

# %%


# %% dataset
targets = ["drer", "dmag", "rsub", "scos"]
train_datasets_x, train_datasets_y, test_datasets_x, test_datasets_y = {}, {}, {}, {}
for target in targets:
    train_datasets_x[f"{target}_random"], train_datasets_y[f"{target}_random"] = get_target_dataset(target, "train", "random")
    train_datasets_x[f"{target}_scaffold"], train_datasets_y[f"{target}_scaffold"] = get_target_dataset(target, "train", "scaffold")
    test_datasets_x[f"{target}_random"], test_datasets_y[f"{target}_random"] = get_target_dataset(target, "test", "random")
    test_datasets_x[f"{target}_scaffold"], test_datasets_y[f"{target}_scaffold"] = get_target_dataset(target, "test", "scaffold")

# %%

res = []
for split in ["scaffold", "random"]:
    print(f"----------------------{split}--------------------------")
    for target in targets:
        print(f"----------{target} train------------")
        train_X, train_Y = train_datasets_x[f"{target}_{split}"], train_datasets_y[f"{target}_{split}"]
        print(f"----------{target} test------------")
        test_X, test_Y = test_datasets_x[f"{target}_{split}"], test_datasets_y[f"{target}_{split}"]

        clf = SVC(probability=True, kernel="rbf", random_state=0)
        params = {'C': (1e-6, 1e+6, 'log-uniform'),
                  'gamma': (1e-6, 1e+1, 'log-uniform'),
                  'kernel': ['linear', 'rbf']}

        search = BayesSearchCV(clf, params, n_iter=30, cv=5, scoring='roc_auc', random_state=32)
        search.fit(train_X, train_Y)
        print("---------finish search---------------")
        clf.set_params(**search.best_params_)

        test_auc = printModelResultWithConfidence(clf, train_X, train_Y, test_X, test_Y)
        joblib.dump(clf, f"SVM_Models1/svm_{split}_{target}.pkl")

        all_mols = pd.read_csv(f"data/merge_{split}_test.csv", usecols=["smiles", f"EC50_{target}"])
        target_mols = all_mols[~np.isnan(all_mols[f'EC50_{target}'])].loc[:, 'smiles'].values

        prob_test_y = clf.predict_proba(test_X)
        prediction = pd.DataFrame({'smiles': target_mols, f'EC50_{target}': prob_test_y[:, 1]})
        prediction.to_csv(f"preds1/svm_{split}_test_{target}_preds.csv", index=False)

        ans = [f"{target}", f"{split}", "SVC"] + test_auc
        res.append(ans)

# %%
targets = ["drer", "scos", "dmag", "rsub"]
res = []
for split in ["scaffold", "random"]:
    print(f"----------------------{split}--------------------------")
    for target in targets:
        print(f"----------{target} train------------")
        train_X, train_Y = train_datasets_x[f"{target}_{split}"], train_datasets_y[f"{target}_{split}"]
        print(f"----------{target} test------------")
        test_X, test_Y = test_datasets_x[f"{target}_{split}"], test_datasets_y[f"{target}_{split}"]
        clf = joblib.load(f"SVM_Models1/svm_{split}0_{target}.pkl")
        test_auc = printModelResultWithConfidence(clf, train_X, train_Y, test_X, test_Y)

        ans = [f"{target}", f"{split}", "SVC"] + test_auc
        res.append(ans)

res_dataset = pd.DataFrame(res, columns=["target", "split", "model", "upper", "lower", "mean", "std", "auc", 'prauc', 'accuracy', 'precision', 'recall', 'f1score'])
res_dataset.to_csv("preds/sklearn_model_SVM_6metrics.csv", index=False)


