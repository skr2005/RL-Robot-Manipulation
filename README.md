# Panda RL Training and Hyperparameters

## WandB Setup

I used wandb to record the success rate of each training. Remember to change the `entity` and `project` in the `train` file to your own name.

To inspect `.wandb` file locally one option is <https://github.com/matomatical/wunderbar>.

## Success Rate Comparison of TQC+HER and SAC+HER

Results seen in the [upstream repository](https://github.com/lsp-yh/RL-Robot-Manipulation/tree/c8ca688cfb4a35ef07b6edb6841c8dc6082d39dd):

| Environment                   | TQC+HER | SAC+HER |
| ----------------------------- | ------- | ------- |
| FrankaPushSparse - v0         | 100.00% | 73.33%  |
| FrankaPushDense - v0          | 100.00% | 0.00%   |
| FrankaSlideSparse - v0        | 0.00%   | 0.00%   |
| FrankaSlideDense - v0         | 20.00%  | 0.00%   |
| FrankaPickAndPlaceSparse - v0 | 100.00% | 0.00%   |
| FrankaPickAndPlaceDense - v0  | 33.33%  | 46.67%  |

Our result:

| Environment                   | TQC+HER | SAC+HER |
| ----------------------------- | ------- | ------- |
| FrankaPushSparse - v0         | 93%     | 100%    |
| FrankaPushDense - v0          | 100%    | 5%      |
| FrankaSlideSparse - v0        | 0%      | 0%      |
| FrankaSlideDense - v0         | 0%      | 0%      |
| FrankaPickAndPlaceSparse - v0 | 27%     | 0%      |
| FrankaPickAndPlaceDense - v0  | 40%     | 20%     |