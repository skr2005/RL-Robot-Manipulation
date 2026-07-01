import os
from gymnasium.envs.registration import register
import importlib

ENV_IDS = []

for task in ["Slide", "Push", "PickAndPlace"]:
    for reward_type in ["sparse", "dense"]:
        reward_suffix = "Dense" if reward_type == "dense" else "Sparse"
        env_id = f"Franka{task}{reward_suffix}-v0"

        from . import envs

        fn = getattr(envs, f"Franka{task}Env")

        register(
            id=env_id,
            entry_point=fn,
            kwargs={"reward_type": reward_type},
            max_episode_steps=50,
        )

        ENV_IDS.append(env_id)
