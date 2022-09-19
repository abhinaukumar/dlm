import numpy as np
from pywt import wavedec2
from dlm_utils import dlm_decouple, dlm_csf_filter, dlm_contrast_mask


def dlm(img_ref, img_dist, wavelet='db2', border_size=0.2, full=False):
    n_levels = 4

    pyr_ref = wavedec2(img_ref, wavelet, 'reflect', n_levels)
    pyr_dist = wavedec2(img_dist, wavelet, 'reflect', n_levels)

    # Ignore approximation coefficients
    del pyr_ref[0], pyr_dist[0]
    # Order wavelet levels from finest to coarsest
    pyr_ref.reverse()
    pyr_dist.reverse()

    pyr_rest, pyr_add = dlm_decouple(pyr_ref, pyr_dist)

    pyr_ref = dlm_csf_filter(pyr_ref)
    pyr_rest = dlm_csf_filter(pyr_rest)
    pyr_add = dlm_csf_filter(pyr_add)

    pyr_rest, pyr_add = dlm_contrast_mask(pyr_rest, pyr_add)

    # Flatten into a list of subbands for convenience
    pyr_ref = [item for sublist in pyr_ref for item in sublist]
    pyr_rest = [item for sublist in pyr_rest for item in sublist]
    pyr_add = [item for sublist in pyr_add for item in sublist]

    # Pool results
    dlm_num = 0
    dlm_den = 0
    for subband in pyr_rest:
        h, w = subband.shape
        border_h = int(border_size*h)
        border_w = int(border_size*w)
        dlm_num += np.power(np.sum(np.power(subband[border_h:-border_h, border_w:-border_w], 3.0)), 1.0/3)
    for subband in pyr_ref:
        h, w = subband.shape
        border_h = int(border_size*h)
        border_w = int(border_size*w)
        dlm_den += np.power(np.sum(np.power(np.abs(subband[border_h:-border_h, border_w:-border_w]), 3.0)), 1.0/3)

    dlm_ret = dlm_num / dlm_den

    if full:
        aim_ret = 0
        count = 0
        for subband in pyr_add:
            h, w = subband.shape
            border_h = int(border_size*h)
            border_w = int(border_size*w)
            aim_ret += np.power(np.sum(np.power(subband[border_h:-border_h, border_w:-border_w], 3.0)), 1.0/3)
            count += (h - 2*border_h)*(w - 2*border_w)
        aim_ret /= count

        comb_ret = dlm_ret - 0.815 * (0.5 - 1.0 / (1.0 + np.exp(1375*aim_ret)))
        ret = (dlm_ret, aim_ret, comb_ret)
    else:
        ret = dlm_ret

    return ret
