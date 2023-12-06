import argparse
import asyncio
import aiohttp
from loguru import logger

from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game, _play_game
from sc2.portconfig import Portconfig
from sc2.client import Client
from sc2.protocol import ConnectionAlreadyClosed


class Game:
    def __init__(
        self, map: str, bot: Bot, opponent: Computer = None, realtime: bool = False
    ):
        self.map = map
        self.bot = bot
        self.opponent = opponent
        self.realtime = realtime

    def start(self) -> None:
        if self.opponent is None:
            raise Exception("No opponent set")
        run_game(
            maps.get(self.map),
            [self.bot, self.opponent],
            realtime=self.realtime,
        )

    async def synchronous_start(self) -> None:
        if self.opponent is None:
            raise Exception("No opponent set")
        await run_game(
            maps.get(self.map),
            [self.bot, self.opponent],
            realtime=self.realtime,
        )

    # Run ladder game
    # This lets python-sc2 connect to a LadderManager game: https://github.com/Cryptyc/Sc2LadderServer
    # Based on: https://github.com/Dentosal/python-sc2/blob/master/examples/run_external.py
    def run_ladder_game(self):
        # Load command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--GamePort", type=int, nargs="?", help="Game port")
        parser.add_argument("--StartPort", type=int, nargs="?", help="Start port")
        parser.add_argument("--LadderServer", type=str, nargs="?", help="Ladder server")
        parser.add_argument(
            "--ComputerOpponent", type=str, nargs="?", help="Computer opponent"
        )
        parser.add_argument("--ComputerRace", type=str, nargs="?", help="Computer race")
        parser.add_argument(
            "--ComputerDifficulty", type=str, nargs="?", help="Computer difficulty"
        )
        parser.add_argument("--OpponentId", type=str, nargs="?", help="Opponent ID")
        parser.add_argument("--RealTime", action="store_true", help="Real time flag")
        args, _unknown = parser.parse_known_args()

        if args.LadderServer is None:
            host = "127.0.0.1"
        else:
            host = args.LadderServer

        host_port = args.GamePort
        lan_port = args.StartPort

        # Add opponent_id to the bot class (accessed through self.opponent_id)
        self.bot.ai.opponent_id = args.OpponentId

        self.realtime = args.RealTime

        # Port config
        if lan_port is None:
            portconfig = None
        else:
            ports = [lan_port + p for p in range(1, 6)]

            portconfig = Portconfig()
            portconfig.server = [ports[1], ports[2]]
            portconfig.players = [[ports[3], ports[4]]]

        # Join ladder game
        g = self.join_ladder_game(
            host=host,
            port=host_port,
            players=[self.bot],
            realtime=self.realtime,
            portconfig=portconfig,
        )

        # Run it
        result = asyncio.get_event_loop().run_until_complete(g)
        return result, args.OpponentId

    # Modified version of sc2.main._join_game to allow custom host and port, and to not spawn an additional sc2process (thanks to alkurbatov for fix)
    async def join_ladder_game(
        host,
        port,
        players,
        realtime,
        portconfig,
        save_replay_as=None,
        game_time_limit=None,
    ):
        ws_url = f"ws://{host}:{port}/sc2api"
        ws_connection = await aiohttp.ClientSession().ws_connect(ws_url, timeout=120)
        client = Client(ws_connection)
        try:
            result = await _play_game(
                players[0], client, realtime, portconfig, game_time_limit
            )
            if save_replay_as is not None:
                await client.save_replay(save_replay_as)
            # await client.leave()
            # await client.quit()
        except ConnectionAlreadyClosed:
            logger.error("Connection was closed before the game ended")
            return None
        finally:
            ws_connection.close()

        return result
