import numpy as np
from int_utils import integral_image_sums


def csf(f):
    return (0.31 + 0.69*f) * np.exp(-0.29*f)


def dlm_decouple(pyr_ref, pyr_dist):
    eps = 1e-30
    n_levels = len(pyr_ref)
    pyr_rest = []
    pyr_add = []

    for level in range(n_levels):
        psi_ref = np.arctan(pyr_ref[level][1] / (pyr_ref[level][0] + eps)) + np.pi*(pyr_ref[level][0] <= 0)
        psi_dist = np.arctan(pyr_dist[level][1] / (pyr_dist[level][0] + eps)) + np.pi*(pyr_dist[level][0] <= 0)

        psi_diff = 180*np.abs(psi_ref - psi_dist)/np.pi
        mask = (psi_diff < 1)
        level_rest = []
        for pyr_ref_sub, pyr_dist_sub in zip(pyr_ref[level], pyr_dist[level]):
            k = np.clip(pyr_dist_sub / (pyr_ref_sub + eps), 0.0, 1.0)
            level_rest.append(k * pyr_ref_sub)
            level_rest[-1][mask] = pyr_dist_sub[mask]

        pyr_rest.append(tuple(level_rest))

    for level_dist, level_rest in zip(pyr_dist, pyr_rest):
        level_add = []
        for i in range(3):
            level_add.append(level_dist[i] - level_rest[i])
        pyr_add.append(tuple(level_add))

    return pyr_rest, pyr_add


def dlm_csf_filter(pyr):
    n_levels = len(pyr)
    filt_pyr = []
    d2h = 3.0  # Distance of height ratio of the display
    pic_height = 1080
    factor = np.pi*pic_height*d2h/180
    level_frequencies = [factor / (1 << (i+1)) for i in range(n_levels)]
    orientation_factors = [1.0, 1.0, 1/(0.85-0.15)]
    for level in range(n_levels):
        filt_level = []
        for i in range(3):
            filt_level.append(pyr[level][i] * csf(level_frequencies[level] * orientation_factors[i]))
        filt_pyr.append(tuple(filt_level))

    return filt_pyr


# Masks pyr_1 using pyr_2
def dlm_contrast_mask_one_way(pyr_1, pyr_2):
    n_levels = len(pyr_1)
    masked_pyr = []
    for level in range(n_levels):
        masking_threshold = 0
        for i in range(3):
            masking_signal = np.abs(pyr_2[level][i])
            # Decompose convolution using contrast masking filter into a local sum operation and an identity operation
            masking_threshold += (integral_image_sums(masking_signal, 3) + masking_signal) / 30
        masked_level = []
        for i in range(3):
            masked_level.append(np.clip(np.abs(pyr_1[level][i]) - masking_threshold, 0, None))
        masked_pyr.append(tuple(masked_level))
    return masked_pyr


# Masks each pyramid using the other
def dlm_contrast_mask(pyr_1, pyr_2):
    masked_pyr_1 = dlm_contrast_mask_one_way(pyr_1, pyr_2)
    masked_pyr_2 = dlm_contrast_mask_one_way(pyr_2, pyr_1)
    return masked_pyr_1, masked_pyr_2
