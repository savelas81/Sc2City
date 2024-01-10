# SC2City

SC2City is a StarCraft II bot designed to compete in the SC2AI Arena ladder using the Terran race. The bot is built in Python using the [BurnySC2](https://github.com/BurnySc2/python-sc2) framework and the MapAnalyzer library.

## Contents

- [Project Structure](#project-structure)
- [Docker Support](#docker-support)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation and Usage](#installation-and-usage)
- [Trainers](#trainers)
- [Limitations](#limitations)

## Project Structure

- `docs`: Contains relevant documents about project architecture, meta information about the game, and other associated documents.
- `docker`: Submodule to the [Starcraft2 Docker](https://github.com/l1h2/Starcraft2-Docker) repository, containing base images to start docker containers.
- `sc2city`: Contains the bot files.
- `tests`: Contains tests for the bot.
- `trainers`: Contains different data extractors for metagame tools and ML trainers.

## Docker Support

The project includes a `docker` directory with a reference to the [Starcraft2 Docker](https://github.com/l1h2/Starcraft2-Docker) repository.

The project itself can also be run from a container and has its own Dockerfile built on top of the [luguenin/starcraft2-base:python_3.11](https://hub.docker.com/layers/luguenin/starcraft2-base/python_3.11/images/sha256-e21b2ddd2181d0b309fd6a17b26b56c13808c4d0da08baf7ef8f069e5a4ca737?context=explore) base image. There are plans to add Dockerfiles for the trainers as well, allowing for running parallel games and improved machine learning support.

To build the Docker image, navigate to the project's root directory and run the following command:

```bash
docker build --rm -t sc2city .
```

The base image comes with the standard ladder maps from the [Blizzard Repository](https://github.com/Blizzard/s2client-proto?tab=readme-ov-file#map-packs). And you can run the project for development with:

```bash
docker run -it --rm sc2city
```

To add different maps from the host machine or from download links the project uses the [luguenin/starcraft2-map_updater](https://hub.docker.com/r/luguenin/starcraft2-map_updater) image. There are two ways to add maps:

- Manually by connecting a volume to running containers at the standard StarCraft II maps folder:

```bash
docker volume create maps

docker run -it --rm -v maps:/home/botuser/StarCraftII/maps sc2city

docker run --rm -v maps:/maps -v "c:/Program Files (x86)/StarCraft II/Maps:/host_maps" -e MAP_LINKS="https://aiarena.net/wiki/184/plugin/attachments/download/35/ https://aiarena.net/wiki/184/plugin/attachments/download/21/" luguenin/starcraft2-map_updater
```

- Using docker compose with [compose.yaml](compose.yaml):

```bash
docker compose up --build
```

After the container is already running and connected to the maps volume you only need to run the command for the map updater to add new maps.

## Features

SC2City has six main agents:

- **Macro Manager**: Handles the macro aspect of the game, choosing strategies and build orders.
- **Micro Manager**: Handles the micro aspect of the game, choosing unit behavior and army scripts.
- **Build Order Manager**: Executes orders given by the Macro Manager, controlling the production of units, structures, and worker behavior.
- **Units Manager**: Executes the scripts chosen by the Micro Manager, controlling combat units.
- **Map Analyzer**: Extracts information from the game map and other visual information and makes it available to the other agents.
- **History Analyzer**: Processes information from past games and other metadata and makes it available to the other agents.

## Prerequisites

The project uses Poetry as a dependency manager. All information on prerequisites can be obtained from the `pyproject.toml` and `poetry.lock` files. However, the bot does require the StarCraft II client to be installed, as well as having the maps used by the bot in the maps folder of the client. Check the [BurnySC2 Repository](https://github.com/BurnySc2/python-sc2#starcraft-ii) for more information on how to install the client and maps or run a container for the project instead.

## Installation and Usage

The bot can be run from [run.py](sc2city/run.py) and configurations about its behavior can be chosen in [settings.json](sc2city/settings.json). The bot also complies with SC2 AI Arena requirements for running in the ladder, so it can be run from the Arena client as well.

## Trainers

There are currently two trainers available, with plans to add more using machine learning. The current trainers are:

- **Burny Build Order**: Extracts build orders created using the [Burny SC2 Planner](https://burnysc2.github.io/sc2-planner/) and saves them as valid build orders for the bot to use.
- **Map Editor**: Allows the user to define building placements using the map editor of StarCraft II and saves them as available building placements for the bot to use. To see the different map pins available and their meanings, check the [building_placements.py](sc2city/game_objects/building_placements.py) file.

## Limitations

The bot is still in early development and can currently only play games on the Dragon Scales map.
