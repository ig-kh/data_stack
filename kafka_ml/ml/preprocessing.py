import numpy as np


def InfiniteImpulseResponseFilter(x, alpha=0.7):
    x_ = x[0]
    x_filt = np.zeros(len(x))
    for i, x_i in enumerate(x[1:]):
        x_filt[i] = alpha * x_i + (1 - alpha) * x_
        x_ = x_filt[i]
    return x_filt
