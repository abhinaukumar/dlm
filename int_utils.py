import numpy as np


def integral_image(x):
    M, N = x.shape
    int_x = np.zeros((M+1, N+1))
    # int_x[1:, 1:] = np.cumsum(np.cumsum(x, 0), 1)
    # Slower, but more precise than cumsum
    for i in range(x.shape[0]):
        int_x[i+1, 1:] = int_x[i, 1:] + x[i, :]
    for j in range(x.shape[1]):
        int_x[:, j+1] = int_x[:, j+1] + int_x[:, j]
    return int_x


def integral_image_sums(x, k, stride=1):
    x_pad = np.pad(x, int((k - stride)/2), mode='reflect')
    int_x = integral_image(x_pad)
    ret = (int_x[:-k:stride, :-k:stride] - int_x[:-k:stride, k::stride] - int_x[k::stride, :-k:stride] + int_x[k::stride, k::stride])
    return ret
