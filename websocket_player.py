#!/usr/bin/env python3
# encoding: utf-8
"""
websocket_player.py

Run an agent in the dotsandboxes_agent directory with websocket communication
protocol used by the user interface available on 
https://github.com/wannesm/dotsandboxes .

Instructions:
- Start agent using `./agent_websocket.py <dir-where-agent-is> 5001`
- Start local server using `./dotsandboxesserver.py 8080`
- Go to `127.0.0.1:8080`
- Enter `ws://127.0.0.1:5001` as one of the agents in the interface
- Start playing

Created by Wannes Meert
Copyright (c) 2022 KU Leuven. All rights reserved.
"""

import sys
import argparse
import logging
import asyncio
import websockets
import json
from collections import defaultdict

import pyspiel
import open_spiel
from tournament import load_agent_from_dir


logger = logging.getLogger(__name__)
games = {}
agentclass = None
agentdir = None


class DotsAndBoxesSocketPlayer:
    """Example Dots and Boxes agent implementation base class.

    A DotsAndBoxesSocketPlayer object should implement the following methods:
    - __init__
    - register_action
    - next_action
    - end_game

    This class does not necessarily use the best data structures for the
    approach you want to use.
    """
    def __init__(self, player, num_rows, num_cols, timelimit):
        """Create Dots and Boxes agent.

        :param player: Player number, 1 or 2
        :param num_rows: Rows in grid
        :param num_cols: Columns in grid
        :param timelimit: Maximum time allowed to send a next action.
        """
        self.player = player
        self.timelimit = timelimit
        self.ended = False
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_cells = (num_rows + 1) * (num_cols + 1)
        dotsandboxes_game_string = (
            "dots_and_boxes(num_rows={},"
            "num_cols={})").format(num_rows, num_cols)
        logger.info("Creating game: {}".format(dotsandboxes_game_string))
        self.game = pyspiel.load_game(dotsandboxes_game_string)
        logger.info(f"Creating agent for Player {self.player}")
        agent1 = load_agent_from_dir(f"Player {self.player}", agentdir)
        if self.player == 1:
            self.agent = agent1['agent_p1']
        elif self.player == 2:
            self.agent = agent1['agent_p2']
        else:
            raise Exception(f"Unknown player: {self.player}")
        self.state = self.game.new_initial_state()

    def register_action(self, row, col, orientation, player):
        """Register action played in game.

        :param row:
        :param col:
        :param orientation: "v" or "h"
        :param player: 1 or 2
        """
        logger.debug(f"Register action player {player}")
        if player == self.player:
            logger.debug("Ignore")
        else:
            action = self.tuple2action(row, col, orientation)
            logger.debug(f"Apply given action {action} for player {player}")
            self.state.apply_action(action)
            self.agent.inform_action(self.state, player, action)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Current state (player {self.state.current_player()}):")
            logger.debug(str(self.state))

    def next_action(self):
        """Return the next action this agent wants to perform.

        :return: (row, column, orientation)
        """
        logger.info("Computing next move (grid={}x{}, player={})"\
                .format(self.num_rows, self.num_cols, self.player))
        current_player = self.state.current_player() + 1
        assert current_player == self.player, f"{current_player} != {self.player}"
        action = self.agent.step(self.state)
        self.state.apply_action(action)
        row, col, orientation = self.action2tuple(action)
        return row, col, orientation

    def end_game(self):
        assert self.state.is_terminal()
        self.ended = True
        logger.info(f"Game ended. Returns = {self.state.returns()}")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"End state (player {self.state.current_player()}):")
            logger.debug(str(self.state))


    def tuple2action(self, row, col, orientation):
        if orientation == "h":
            action = row * self.num_cols + col
        else:
            action = (self.num_rows + 1) * self.num_cols + row * (self.num_cols + 1) + col
        return action


    def action2tuple(self, action):
        nb_hlines = (self.num_rows + 1) * self.num_cols
        if action < nb_hlines:
            row = action // self.num_cols
            col = action % self.num_cols
            orientation = 'h'
        else:
            action2 = action - nb_hlines
            row = action2 // (self.num_cols + 1)
            col = action2 % (self.num_cols + 1)
            orientation = 'v'
        return row, col, orientation


async def handler(websocket, path):
    logger.info("Start listening")
    game = None
    # msg = await websocket.recv()
    try:
        async for msg in websocket:
            logger.info("< {}".format(msg))
            try:
                msg = json.loads(msg)
            except json.decoder.JSONDecodeError as err:
                logger.error(err)
                return False
            game = msg["game"]
            answer = None
            if msg["type"] == "start":
                # Initialize game
                if msg["game"] in games:
                    raise Exception(f"Game {msg['game']} already running")
                else:
                    num_rows, num_cols = msg["grid"]
                    games[msg["game"]] = agentclass(msg["player"],
                                                    num_rows,
                                                    num_cols,
                                                    msg["timelimit"])
                if msg["player"] == 1:
                    # Start the game
                    nm = games[game].next_action()
                    # print('nm = {}'.format(nm))
                    if nm is None:
                        # Game over
                        logger.info("Game over")
                        continue
                    r, c, o = nm
                    answer = {
                        'type': 'action',
                        'location': [r, c],
                        'orientation': o
                    }
                else:
                    # Wait for the opponent
                    answer = None

            elif msg["type"] == "action":
                # An action has been played
                r, c = msg["location"]
                o = msg["orientation"]
                games[game].register_action(r, c, o, msg["player"])
                if msg["nextplayer"] == games[game].player:
                    # Compute your move
                    nm = games[game].next_action()
                    if nm is None:
                        # Game over
                        logger.info("Game over")
                        continue
                    nr, nc, no = nm
                    answer = {
                        'type': 'action',
                        'location': [nr, nc],
                        'orientation': no
                    }
                else:
                    answer = None

            elif msg["type"] == "end":
                # End the game
                r, c = msg["location"]
                o = msg["orientation"]
                games[game].register_action(r, c, o, msg["player"])
                games[game].end_game()
                answer = None
            else:
                logger.error("Unknown message type:\n{}".format(msg))

            if answer is not None:
                await websocket.send(json.dumps(answer))
                logger.info("> {}".format(answer))
    except websockets.exceptions.ConnectionClosed as err:
        logger.info("Connection closed")
    logger.info("Exit handler")


async def start_server(port):
    async with websockets.serve(handler, "localhost", port):
        print("Running on ws://127.0.0.1:{}".format(port))
        await asyncio.Future()  # run forever


def main(argv=None):
    global agentclass
    global agentdir
    parser = argparse.ArgumentParser(description='Start agent to play Dots and Boxes')
    parser.add_argument('agent1_dir', help='Path to agent directory')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Verbose output')
    parser.add_argument('--quiet', '-q', action='count', default=0, help='Quiet output')
    parser.add_argument('port', metavar='PORT', type=int, help='Port to use for server')
    args = parser.parse_args(argv)

    logger.setLevel(max(logging.INFO - 10 * (args.verbose - args.quiet), logging.DEBUG))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    agentdir = args.agent1_dir
    agentclass = DotsAndBoxesSocketPlayer
    asyncio.run(start_server(args.port))


if __name__ == "__main__":
    sys.exit(main())

