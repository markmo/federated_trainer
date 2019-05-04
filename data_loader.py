import numpy as np
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).parent


class DataLoader(object):

    def __init__(self):
        self.x, self.y, self.x_test, self.y_test = None, None, None, None
        self.seed = 42
        np.random.seed(self.seed)

    def load_data(self):
        data = pd.read_csv(ROOT_DIR / 'data/data.csv', sep='\t')
        x = data[data.columns[:-1]]

        # add constant for intercept
        x[len(data.columns)] = 1
        y = data[data.columns[-1]]
        self.x = x.values
        self.y = y.values

        # shuffle
        rand_idxs = np.random.permutation(x.shape[0])
        x, y = self.x[rand_idxs, :], self.y[rand_idxs]

        test_size = int(len(self.x) * .2)
        test_idxs = np.random.choice(x.shape[0], size=test_size, replace=False)
        x_test, y_test = x[test_idxs, :], y[test_idxs]
        x_train, y_train = x[~test_idxs, :], y[~test_idxs]
        return x_train.tolist(), y_train.tolist(), x_test.tolist(), y_test.tolist()

    def get_data(self):
        return self.x, self.y
