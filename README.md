# Panda RL Training and Hyperparameters

## Quick Start

The code is only tested through Python 3.11.9. Other versions of Python is possible to work or not to work.

An incomplete specification for dependencies is at `./requirements.txt`. You can replace PyTorch to utilize GPU for training. See <https://pytorch.org/get-started/locally/> for more details.

The code to train and test has been modified into a module. To start, you may want:

```shell
cd ..
python -m RL-Robot-Manipulation
```

## WandB Setup

Wandb is used to record the success rate of each training. Remember to change the `entity` and `project` in the `train` file to your own name.

To inspect `.wandb` file locally one option is <https://github.com/matomatical/wunderbar>.

## Success Rate Comparison of TQC+HER and SAC+HER

Results from "Table II" in <https://arxiv.org/abs/2312.13788>:

|   Tasks           |   DDPG        |   SAC         |   TQC         |
| ----------------- | ------------- | ------------- | ------------- |
|   Push            |   11.7±0.3    |   100±0.0     |   100±0.0     |
|   Slide           |   71.7±0.5    |   85.0±0.4    |   85.1±0.4    |
|   Pick & Place    |   58.3±0.4    |   75.0±0.5    |   100.0±0.0   |

Results seen in [the upstream repository](https://github.com/lsp-yh/RL-Robot-Manipulation/tree/c8ca688cfb4a35ef07b6edb6841c8dc6082d39dd):

| Environment                   | TQC+HER | SAC+HER |
| ----------------------------- | ------- | ------- |
| FrankaPushSparse - v0         | 100.00% | 73.33%  |
| FrankaPushDense - v0          | 100.00% | 0.00%   |
| FrankaSlideSparse - v0        | 0.00%   | 0.00%   |
| FrankaSlideDense - v0         | 20.00%  | 0.00%   |
| FrankaPickAndPlaceSparse - v0 | 100.00% | 0.00%   |
| FrankaPickAndPlaceDense - v0  | 33.33%  | 46.67%  |

Our results:

| Environment                   | TQC+HER | SAC+HER |
| ----------------------------- | ------- | ------- |
| FrankaPushSparse - v0         | 100%    | 93%     |
| FrankaPushDense - v0          | 93%     | 0%      |
| FrankaSlideSparse - v0        | 0%      | 0%      |
| FrankaSlideDense - v0         | 0%      | 0%      |
| FrankaPickAndPlaceSparse - v0 | 27%     | 0%      |
| FrankaPickAndPlaceDense - v0  | 40%     | 20%     |