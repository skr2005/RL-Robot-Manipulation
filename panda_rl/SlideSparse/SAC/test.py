import os

os.environ["MUJOCO_GL"] = "glfw"  # Use glfw rendering for windowed display

import gymnasium as gym
from stable_baselines3 import SAC
import numpy as np
from .... import panda_mujoco_gym  # 注册环境
from stable_baselines3.common.vec_env import DummyVecEnv
import time


class TerminateOnTruncatedWrapper(gym.Wrapper):
    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        if truncated:
            terminated = True
        return obs, reward, terminated, truncated, info


def make_env(reward_type="sparse"):
    env = gym.make("FrankaSlideSparse-v0", reward_type=reward_type, render_mode="human")
    env = TerminateOnTruncatedWrapper(env)
    return env


test_env = DummyVecEnv([lambda: make_env()])
model = SAC.load("sac_franka_slide_sparse_final", env=test_env)

n_episodes = 20
success_count = 0

for episode in range(n_episodes):
    obs = test_env.reset()
    done = False
    episode_success = False

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        results = test_env.step(action)

        if len(results) == 4:
            obs, reward, done, info = results
            terminated = [done]
            truncated = [False]
        else:
            obs, reward, terminated, truncated, info = results

        if isinstance(terminated, bool):
            terminated = [terminated]
        if isinstance(truncated, bool):
            truncated = [truncated]

        done = terminated[0] or truncated[0]

        test_env.render()
        time.sleep(0.1)

        if isinstance(info, list):
            info = info[0]
        if info.get("is_success", False):
            episode_success = True

    if episode_success:
        success_count += 1

    print(f"Episode {episode + 1}: {'Success' if episode_success else 'Fail'}")

print(f"\nSuccess rate: {success_count / n_episodes * 100:.1f}%")
test_env.close()
