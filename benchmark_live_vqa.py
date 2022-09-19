import numpy as np
import cv2
from dlm import dlm

from scipy.io import loadmat, savemat
from scipy.stats import spearmanr, pearsonr
from scipy.optimize import curve_fit

import pandas as pd
import os
import argparse

import progressbar

parser = argparse.ArgumentParser(description="Code to benchmark DLM on the LIVE VQA Database")
parser.add_argument("--path", help="Path to database", required=True)
parser.add_argument("--algorithm", help="Algorithm to run", type=str, required=True, choices=['dlm', 'aim', 'comb'])
parser.add_argument("--wavelet", help="Wavelet to use", type=str, default="db2")
args = parser.parse_args()

f = loadmat('data/live_vqa_scores.mat')
scores = f['scores'].squeeze()
scores = (scores - np.min(scores))/(np.max(scores) - np.min(scores))

df = pd.read_csv(os.path.join(args.path, 'live_video_quality_seqs.txt'), header=None, engine='python')
file_list = df.values[:, 0]

refs = ["pa", "rb", "rh", "tr", "st", "sf", "bs", "sh", "mc", "pr"]
fps = [25, 25, 25, 25, 25, 25, 25, 50, 50, 50]
fps = [str(f) + 'fps' for f in fps]

n_refs = len(refs)

widgets = [
    progressbar.ETA(),
    progressbar.Bar(),
    ' ', progressbar.DynamicMessage('file'),
    '/', progressbar.DynamicMessage('total')
]

quals = np.zeros((n_refs*15,))
k = 0

with progressbar.ProgressBar(max_value=n_refs*15, widgets=widgets) as bar:
    for i_ref, ref in enumerate(refs):
        v_ref = cv2.VideoCapture(os.path.join(args.path, 'videos', ref + '_Folder', 'rgb', ref + '1' + '_' + fps[i_ref] + '.mp4'))
        w = int(v_ref.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(v_ref.get(cv2.CAP_PROP_FRAME_HEIGHT))
        for i_dist in range(2, 17):
            v_dist = cv2.VideoCapture(os.path.join(args.path, 'videos', ref + '_Folder', 'rgb', ref + str(i_dist) + '_' + fps[i_ref] + '.mp4'))
            frame_quals = []
            while(v_ref.isOpened() and v_dist.isOpened()):
                ret_ref, rgb_ref = v_ref.read()
                ret_dist, rgb_dist = v_dist.read()

                if ret_ref and ret_dist:
                    y_ref = cv2.cvtColor(rgb_ref, cv2.COLOR_BGR2YUV)[:, :, 0].astype('float32')
                    y_dist = cv2.cvtColor(rgb_dist, cv2.COLOR_BGR2YUV)[:, :, 0].astype('float32')

                    if args.algorithm == 'dlm':
                        frame_quals.append(dlm(y_ref, y_dist, args.wavelet))
                    elif args.algorithm == 'aim':
                        frame_quals.append(dlm(y_ref, y_dist, args.wavelet, full=True)[1])
                    else:
                        frame_quals.append(dlm(y_ref, y_dist, args.wavelet, full=True)[2])
                else:
                    break

            quals[k] = np.mean(frame_quals)
            k += 1
            v_ref.set(cv2.CAP_PROP_POS_FRAMES, 0)
            bar.update(i_ref*15 + i_dist - 2, file=i_ref*15+i_dist-1, total=n_refs*15)

# Fitting logistic function to scores
[[b0, b1, b2, b3, b4], _] = curve_fit(lambda t, b0, b1, b2, b3, b4: b0 * (0.5 - 1.0/(1 + np.exp(b1*(t - b2))) + b3 * t + b4),
                                      quals, scores, p0=0.5*np.ones((5,)), maxfev=20000)

scores_pred = b0 * (0.5 - 1.0/(1 + np.exp(b1*(quals - b2))) + b3 * quals + b4)

pcc = pearsonr(scores_pred, scores)[0]
srocc = spearmanr(scores_pred, scores)[0]
rmse = np.sqrt(np.mean((scores_pred - scores)**2))

print("PCC:", pcc)
print("SROCC:", srocc)
print("RMSE:", rmse)

savemat('data/live_vqa_' + args.wavelet + '_' + args.algorithm + 's.mat', {args.algorithm + 's': quals, 'pcc': pcc, 'srocc': srocc, 'rmse': rmse})
