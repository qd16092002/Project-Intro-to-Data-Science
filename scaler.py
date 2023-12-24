import numpy as np
import torch


class Scaler:
    def __init__(self, min_value=0, lower_bound=100_000_000, upper_bound=1_000_000_000_000, scaling=1_000_000_000):
        self.scaling = scaling
        self.lower_bound = lower_bound / scaling
        self.upper_bound = upper_bound / scaling
        self.min_value = min_value

    def transform(self, data):
        if not isinstance(data, np.ndarray):
            raise ValueError()

        assert len(data.shape) == 2

        data = data/self.scaling
        scaled_data = (data - self.lower_bound) / \
            (self.upper_bound - self.lower_bound) + self.min_value
        return scaled_data

    def invert_transform(self, scaled_data):
        if not isinstance(scaled_data, np.ndarray):
            raise ValueError()

        assert len(scaled_data.shape) == 2

        data = (scaled_data - self.min_value) * \
            (self.upper_bound - self.lower_bound) + self.lower_bound
        data = data*self.scaling
        return data
    