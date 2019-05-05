import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.datasets import load_diabetes

ROOT_DIR = Path(__file__).parent


class DataLoader(object):

    def __init__(self):
        logging.info('init')
        self.x, self.y, self.x_test, self.y_test = None, None, None, None
        self.seed = 42
        np.random.seed(self.seed)

    def load_data(self):
        logging.info(self.load_data.__name__)
        data = pd.read_csv(ROOT_DIR / 'data/data.csv', sep='\t')
        x = data[data.columns[:-1]]

        # add constant for intercept
        x[len(data.columns)] = 1
        y = data[data.columns[-1]]
        self.x = np.asarray(x.values.tolist())
        self.y = np.asarray(y.values.tolist())

        # shuffle
        # rand_idxs = np.random.permutation(x.shape[0])
        # x, y = self.x[rand_idxs, :], self.y[rand_idxs]

        # test_size = int(len(self.x) * .2)
        # test_idx = np.random.choice(x.shape[0], size=test_size, replace=False)
        # train_idx = np.ones(x.shape[0], dtype=bool)
        # train_idx[test_idx] = False
        # x_test, y_test = x[test_idx, :], y[test_idx]
        # x_train, y_train = x[train_idx, :], y[train_idx]

        # return x_train, y_train, x_test, y_test

    def get_data(self):
        logging.info(self.get_data.__name__)
        return self.x, self.y

    def load_diabetes_data(self):
        logging.info(self.load_diabetes_data.__name__)
        diabetes_dataset = load_diabetes()
        x = diabetes_dataset.data
        y = diabetes_dataset.target

        # add constant for intercept
        x = np.c_[x, np.ones(x.shape[0])]

        # shuffle
        rand_idxs = np.random.permutation(x.shape[0])
        x, y = x[rand_idxs, :], y[rand_idxs]

        test_size = int(len(x) * .2)
        test_idx = np.random.choice(x.shape[0], size=test_size, replace=False)
        train_idx = np.ones(x.shape[0], dtype=bool)
        train_idx[test_idx] = False
        x_test, y_test = x[test_idx, :], y[test_idx]
        x_train, y_train = x[train_idx, :], y[train_idx]

        # split training set amongst multiple clients
        # The selection is not at random. We simulate the fact that each client
        # sees a potentially very different sample of patients.
        # x, y = {}, {}
        # step = int(x_train.shape[0] / n_subsets)
        # for i in range(n_subsets):
        #     x[i] = x_train[step * i: step * (i + 1), :]
        #     y[i] = y_train[step * i: step * (i + 1)]

        return x_train, y_train, x_test, y_test
