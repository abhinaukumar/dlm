# A Python Implementation of the Detail Loss Metric

This code implements the Detail Loss and Additive Impairment Metrics proposed in
> S. Li, F. Zhang, L. Ma and K. N. Ngan, "Image Quality Assessment by Separately Evaluating Detail Losses and Additive Impairments," in IEEE Transactions on Multimedia, vol. 13, no. 5, pp. 935-949, Oct. 2011, doi: 10.1109/TMM.2011.2152382.

## Applications
DLM forms an important component of the [Video Multimethod Assessment Fusion](https://github.com/Netflix/vmaf) (VMAF) algorithm, which is the current industry standard for quality assessment of compressed videos.

A modified version of DLM has also been used in the efficient fusion-based quality assessment model [FUNQUE](https://github.com/abhinaukumar/funque), which has been proposed as an improvement over VMAF.

## Performance on Subjective Databases
### LIVE Image Quality Database
PCC: 0.9258

SROCC: 0.9112

RMSE: 0.1034

### LIVE Video Quality Database
PCC: 0.64038

SROCC: 0.6848

RMSE: 0.1679
