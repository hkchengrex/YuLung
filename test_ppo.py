# Taken directly from https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail

import copy
import glob
import os
import time
from collections import deque
from collections import namedtuple
SVSpec = namedtuple('SVSpec', ['type', 'index', 'scale'])

import gym
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from a2c_ppo_acktr import algo, utils
from a2c_ppo_acktr.algo import gail
from a2c_ppo_acktr.arguments import get_args
from a2c_ppo_acktr.envs import make_vec_envs
from a2c_ppo_acktr.model import Policy
from a2c_ppo_acktr.storage import RolloutStorage
from evaluation import evaluate
from pysc2.lib import actions, features
from pysc2.env import sc2_env
import envs

from feature.py_feature import FeatureTransform
from bot.macro_actions import NUMBER_EXPANSIONS

import logging
from tensorboardX import SummaryWriter
import datetime

def main():
    args = get_args()

    full_id = args.expr_id + '_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    cf_logger = logging.getLogger()

    cf_logger.handlers = []

    fileHandler = logging.FileHandler("log/{0}.log".format(full_id))
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.INFO)
    cf_logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.WARNING)
    cf_logger.addHandler(consoleHandler)

    logger = SummaryWriter(os.path.join('log', full_id))

    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    max_reward = -10000

    if args.cuda and torch.cuda.is_available() and args.cuda_deterministic:
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True

    log_dir = os.path.expanduser(args.log_dir)
    eval_log_dir = log_dir + "_eval"
    utils.cleanup_log_dir(log_dir)
    utils.cleanup_log_dir(eval_log_dir)

    torch.set_num_threads(1)

    device = torch.device("cuda:0" if args.cuda else "cpu")

    envs = make_vec_envs(args.env_name, args.seed, args.num_processes,
                         args.gamma, args.log_dir, device, False)

    # (obs)  Define the Screen Observation Space

    # 1. Defined by pysc2
    # screen_0 = features.SCREEN_FEATURES.player_relative

    # 2. Defined by custom
    # Required Field
    # a. type (features.FeatureType.CATEGORICAL / features.FeatureType.SCALAR)
    # b. scale (For categorical, it is the number of classes, for scalar it is used to
    #    perform log transform as in Pysc2 paper)
    # (Other Just Fill Anythings)
    screen_0 = features.SCREEN_FEATURES.height_map
    screen_1 = features.SCREEN_FEATURES.visibility_map
    screen_2 = features.SCREEN_FEATURES.creep
    screen_3 = features.SCREEN_FEATURES.player_relative
    screen_4 = features.SCREEN_FEATURES.unit_density_aa
    screen_5 = features.SCREEN_FEATURES.unit_hit_points

    # screen_0 = features.Feature(type=features.FeatureType.CATEGORICAL, scale=6, name="", layer_set=None, full_name=None,
    #                             palette=None, clip=False
    #                             , index=0)
    # screen_1 = features.Feature(type=features.FeatureType.SCALAR, scale=3, name="", layer_set=None, full_name=None,
    #                             palette=None, clip=False
    #                             , index=0)

    # Define the Info Observation Space
    # Required Field
    # [0]. features.FeatureType.CATEGORICAL / features.FeatureType.SCALAR
    # [1]. index
    # [2]. scale (For categorical, it is the number of classes, it is used to
    #    perform log transform as in Pysc2 paper)

    info_discrete = []
    for i in range(FeatureTransform.n_non_screen_cate()):
        if i < NUMBER_EXPANSIONS:
            info_discrete.append(SVSpec(features.FeatureType.CATEGORICAL, i, 3))
        else:
            info_discrete.append(SVSpec(features.FeatureType.CATEGORICAL, i, 2))

    info_scalar = [
        SVSpec(features.FeatureType.SCALAR, 0 + len(info_discrete), 24),
        SVSpec(features.FeatureType.SCALAR, 1 + len(info_discrete), 3000),
        SVSpec(features.FeatureType.SCALAR, 2 + len(info_discrete), 30),
        SVSpec(features.FeatureType.SCALAR, 3 + len(info_discrete), 5000),
        SVSpec(features.FeatureType.SCALAR, 4 + len(info_discrete), 3000),
        SVSpec(features.FeatureType.SCALAR, 5 + len(info_discrete), 200),
        SVSpec(features.FeatureType.SCALAR, 6 + len(info_discrete), 200),
    ]

    # ####

    actor_critic = Policy(
        envs.observation_space,
        envs.action_space,
        # (obs) Copy the above definition to this ##
        [screen_0, screen_1, screen_2, screen_3, screen_4, screen_5],
        info_discrete + info_scalar,
        # ####
        base_kwargs={'recurrent': args.recurrent_policy})

    if args.load_model is not None:
        actor_critic.load_state_dict(torch.load(args.load_model))

    actor_critic.to(device)

    if args.algo == 'a2c':
        agent = algo.A2C_ACKTR(
            actor_critic,
            args.value_loss_coef,
            args.entropy_coef,
            lr=args.lr,
            eps=args.eps,
            alpha=args.alpha,
            max_grad_norm=args.max_grad_norm)
    elif args.algo == 'ppo':
        agent = algo.PPO(
            actor_critic,
            args.clip_param,
            args.ppo_epoch,
            args.num_mini_batch,
            args.value_loss_coef,
            args.entropy_coef,
            lr=args.lr,
            eps=args.eps,
            max_grad_norm=args.max_grad_norm)
    elif args.algo == 'acktr':
        agent = algo.A2C_ACKTR(
            actor_critic, args.value_loss_coef, args.entropy_coef, acktr=True)

    if args.gail:
        assert len(envs.observation_space.shape) == 1
        discr = gail.Discriminator(
            envs.observation_space.shape[0] + envs.action_space.shape[0], 100,
            device)
        file_name = os.path.join(
            args.gail_experts_dir, "trajs_{}.pt".format(
                args.env_name.split('-')[0].lower()))

        gail_train_loader = torch.utils.data.DataLoader(
            gail.ExpertDataset(
                file_name, num_trajectories=4, subsample_frequency=20),
            batch_size=args.gail_batch_size,
            shuffle=True,
            drop_last=True)

    rollouts = RolloutStorage(args.num_steps, args.num_processes,
                              envs.observation_space, envs.action_space,
                              actor_critic.recurrent_hidden_state_size)

    obs = envs.reset()

    #####
    image_data = obs['feature_screen']
    non_image_data = obs['info_discrete']

    rollouts.image[0].copy_(image_data)
    rollouts.non_image[0].copy_(non_image_data)
    ########

    rollouts.to(device)

    episode_rewards = deque(maxlen=10)

    start = time.time()
    num_updates = int(
        args.num_env_steps) // args.num_steps // args.num_processes
    for j in range(num_updates):

        if args.use_linear_lr_decay:
            # decrease learning rate linearly
            utils.update_linear_schedule(
                agent.optimizer, j, num_updates,
                agent.optimizer.lr if args.algo == "acktr" else args.lr)

        for step in range(args.num_steps):
            # Sample actions
            with torch.no_grad():

                ########
                value, dis_action, con_action, action_log_prob, recurrent_hidden_states = actor_critic.act(
                    rollouts.image[step], rollouts.non_image[step], rollouts.recurrent_hidden_states[step],
                    rollouts.masks[step])
                ########

            ####
            # Obser reward and next obs
            if con_action is None:
                action = {"discrete_output": dis_action.cpu().numpy()}
            else:
                action = {"discrete_output": dis_action.cpu().numpy(),
                          "continuous_output": con_action.cpu().numpy()}
            obs, reward, done, infos = envs.step(action)
            ####

            for info in infos:
                if 'episode' in info.keys():
                    episode_rewards.append(info['episode']['r'])

            # If done then clean the history of observations.
            masks = torch.FloatTensor(
                [[0.0] if done_ else [1.0] for done_ in done])
            bad_masks = torch.FloatTensor(
                [[0.0] if 'bad_transition' in info.keys() else [1.0]
                 for info in infos])

            ########
            rollouts.insert(obs['feature_screen'], obs['info_discrete'], recurrent_hidden_states, dis_action, con_action,
                            action_log_prob, value, reward, masks, bad_masks)
            ########

        with torch.no_grad():

            ########
            next_value = actor_critic.get_value(
                rollouts.image[step], rollouts.non_image[step], rollouts.recurrent_hidden_states[-1],
                rollouts.masks[-1]).detach()
            ########

        if args.gail:
            if j >= 10:
                envs.venv.eval()

            gail_epoch = args.gail_epoch
            if j < 10:
                gail_epoch = 100  # Warm up
            for _ in range(gail_epoch):
                discr.update(gail_train_loader, rollouts,
                             utils.get_vec_normalize(envs)._obfilt)

            ########
            for step in range(args.num_steps):
                rollouts.rewards[step] = discr.predict_reward(
                    rollouts.image[step], rollouts.non_image[step], rollouts.dis_actions[step], rollouts.con_actions[step], args.gamma,
                    rollouts.masks[step])
             ########

        rollouts.compute_returns(next_value, args.use_gae, args.gamma,
                                 args.gae_lambda, args.use_proper_time_limits)

        value_loss, action_loss, dist_entropy = agent.update(rollouts)

        logger.add_scalar('stat/value_loss', value_loss, j)
        logger.add_scalar('stat/action_loss', action_loss, j)
        logger.add_scalar('stat/entropy', dist_entropy, j)

        print('Value   loss: ', value_loss)
        print('Action  loss: ', action_loss)
        print('Entropy loss: ', dist_entropy)

        rollouts.after_update()

        # save for every interval-th episode or for the last epoch
        if (j % args.save_interval == 0
                or j == num_updates - 1) and args.save_dir != "":
            save_path = os.path.join(args.save_dir, full_id + args.algo)
            try:
                os.makedirs(save_path)
            except OSError:
                pass

            # torch.save([
            #     actor_critic,
            #     getattr(utils.get_vec_normalize(envs), 'ob_rms', None)
            # ], os.path.join(save_path, args.env_name + '_%d' % j + ".pt"))

            torch.save(
                actor_critic.state_dict(), os.path.join(save_path, args.env_name + '_%d' % j + ".pt"))

        if j % args.log_interval == 0 and len(episode_rewards) > 1:
            total_num_steps = (j + 1) * args.num_processes * args.num_steps
            end = time.time()
            print(
                "Updates {}, num timesteps {}, FPS {} \n Last {} training episodes: mean/median reward {:.1f}/{:.1f}, min/max reward {:.1f}/{:.1f}\n"
                .format(j, total_num_steps,
                        int(total_num_steps / (end - start)),
                        len(episode_rewards), np.mean(episode_rewards),
                        np.median(episode_rewards), np.min(episode_rewards),
                        np.max(episode_rewards), dist_entropy, value_loss,
                        action_loss))

            mean_reward = np.mean(episode_rewards)
            logger.add_scalar('reward/mean_reward', mean_reward, j)
            logger.add_scalar('reward/median_reward', np.median(episode_rewards), j)
            logger.add_scalar('reward/min_reward', np.min(episode_rewards), j)
            logger.add_scalar('reward/max_reward', np.max(episode_rewards), j)

            if mean_reward > max_reward:
                save_path = os.path.join(args.save_dir, full_id + args.algo)
                try:
                    os.makedirs(save_path)
                except OSError:
                    pass

                torch.save(
                    actor_critic.state_dict(), os.path.join(save_path, args.env_name + '_best' + ".pt"))

                max_reward = mean_reward

        if (args.eval_interval is not None and len(episode_rewards) > 1
                and j % args.eval_interval == 0):
            ob_rms = utils.get_vec_normalize(envs).ob_rms
            evaluate(actor_critic, ob_rms, args.env_name, args.seed,
                     args.num_processes, eval_log_dir, device)


if __name__ == "__main__":
    main()
