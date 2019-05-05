import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.datasets import load_diabetes, load_iris

ROOT_DIR = Path(__file__).parent

TEST_SET_RATIO = .15


class DataLoader(object):

    def __init__(self):
        logging.info('init')
        self.x, self.y, self.x_test, self.y_test = None, None, None, None
        self.seed = 42
        np.random.seed(self.seed)

    def load_data(self, header=None, sep='\t'):
        logging.info(self.load_data.__name__)
        data = pd.read_csv('data/data.csv', header=header, sep=sep)
        x = data[data.columns[:-1]]

        # add constant for intercept
        x[len(data.columns)] = 1
        y = data[data.columns[-1]]

        # scale features
        # x = np.apply_along_axis(self.scale, 0, x)

        self.x = np.asarray(x.values.tolist())
        self.y = np.asarray(y.values.tolist())

        # shuffle
        # rand_idxs = np.random.permutation(x.shape[0])
        # x, y = self.x[rand_idxs, :], self.y[rand_idxs]

        # test_size = int(len(self.x) * TEST_SET_RATIO)
        # test_idx = np.random.choice(x.shape[0], size=test_size, replace=False)
        # train_idx = np.ones(x.shape[0], dtype=bool)
        # train_idx[test_idx] = False
        # x_test, y_test = x[test_idx, :], y[test_idx]
        # x_train, y_train = x[train_idx, :], y[train_idx]

        # return x_train, y_train, x_test, y_test

    @staticmethod
    def scale(x):
        return (x - x.mean()) / x.std()

    def get_data(self):
        logging.info(self.get_data.__name__)
        return self.x, self.y

    def prepare_data(self, x, y):
        # add constant for intercept
        x = np.c_[x, np.ones(x.shape[0])]

        # scale features
        # x = np.apply_along_axis(self.scale, 0, x)

        # shuffle
        rand_idxs = np.random.permutation(x.shape[0])
        x, y = x[rand_idxs, :], y[rand_idxs]

        test_size = int(len(x) * TEST_SET_RATIO)
        test_idx = np.random.choice(x.shape[0], size=test_size, replace=False)
        train_idx = np.ones(x.shape[0], dtype=bool)
        train_idx[test_idx] = False
        x_test, y_test = x[test_idx, :], y[test_idx]
        x_train, y_train = x[train_idx, :], y[train_idx]

        return x_train, y_train, x_test, y_test

    def load_iris_data(self):
        """ Classification set """
        logging.info(self.load_iris_data.__name__)
        iris_dataset = load_iris()
        x = iris_dataset.data
        y = iris_dataset.target

        return self.prepare_data(x, y)

    def load_diabetes_data(self):
        """ Regression set """
        logging.info(self.load_diabetes_data.__name__)
        diabetes_dataset = load_diabetes()
        x = diabetes_dataset.data
        y = diabetes_dataset.target

        return self.prepare_data(x, y)

        # add constant for intercept
        # x = np.c_[x, np.ones(x.shape[0])]

        # shuffle
        # rand_idxs = np.random.permutation(x.shape[0])
        # x, y = x[rand_idxs, :], y[rand_idxs]

        # test_size = int(len(x) * TEST_SET_RATIO)
        # test_idx = np.random.choice(x.shape[0], size=test_size, replace=False)
        # train_idx = np.ones(x.shape[0], dtype=bool)
        # train_idx[test_idx] = False
        # x_test, y_test = x[test_idx, :], y[test_idx]
        # x_train, y_train = x[train_idx, :], y[train_idx]

        # split training set amongst multiple clients
        # The selection is not at random. We simulate the fact that each client
        # sees a potentially very different sample of patients.
        # x, y = {}, {}
        # step = int(x_train.shape[0] / n_subsets)
        # for i in range(n_subsets):
        #     x[i] = x_train[step * i: step * (i + 1), :]
        #     y[i] = y_train[step * i: step * (i + 1)]

        # return x_train, y_train, x_test, y_test
