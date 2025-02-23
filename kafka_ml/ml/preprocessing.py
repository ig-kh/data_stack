import numpy as np


def partial_vectorize(data, static_cols=[]):
    return {
        "seq": np.stack(
            [np.asarray(l) for l in zip(*data.drop(columns=static_cols).values.T)]
        ),
        "stat": data[static_cols].values,
    }


class InfiniteImpulseResponseFilter:
    def __init__(self, alpha=0.7):
        self.alpha = alpha

    def impl(self, x):
        x_ = x[0]
        x_filt = np.zeros(len(x))
        for i, x_i in enumerate(x[1:]):
            x_filt[i] = self.alpha * x_i + (1 - self.alpha) * x_
            x_ = x_filt[i]
        return x_filt

    def __call__(self, batch):
        return np.stack([self.impl(sample) for sample in batch])
