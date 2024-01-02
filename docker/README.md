# StarCraft II Docker Image

This Docker image provides a base Linux environment for running StarCraft II bots. It is built on top of the [Python 3.11.6-slim](https://hub.docker.com/layers/library/python/3.11.6-slim/images/sha256-38a28170d13a276d42b7dd55cae54440b581d773549d361d19089ec47d4791c5?context=explore) image and includes all necessary files and dependencies to run StarCraft II.

It uses the 4.1.0 Linux version of the game available in the official [Blizzard Repository](https://github.com/Blizzard/s2client-proto?tab=readme-ov-file#linux-packages) and comes with all the [standard ladder maps](https://github.com/Blizzard/s2client-proto?tab=readme-ov-file#map-packs).

## Building the Image

To build the Docker image, navigate to the directory containing the Dockerfile and run the following command:

```bash
docker build --rm -t starcraft2-base .
```

Or to build it from the project's root directory:

```bash
docker build --rm -t starcraft2-base ./docker
```

The image will also extract the latest maps from the [SC2 AI Arena](https://aiarena.net/wiki/maps/) wiki. However, you can also specify a different map link or a list of map links at build time using the `MAP_LINKS` build argument.

- Single link:

```bash
docker build --rm -t starcraft2-base --build-arg MAP_LINKS=https://aiarena.net/wiki/184/plugin/attachments/download/35/ ./docker
```

- Multiple links:

```bash
docker build --rm -t starcraft2-base --build-arg MAP_LINKS="https://aiarena.net/wiki/184/plugin/attachments/download/35/ https://aiarena.net/wiki/184/plugin/attachments/download/36/" ./docker
```

If no argument is provided, the [default value](https://aiarena.net/wiki/184/plugin/attachments/download/35/) will be used.
