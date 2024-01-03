FROM python:3.11.6-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y wget unzip

RUN adduser --disabled-password --gecos "" botuser && chown -R botuser /home/botuser
USER botuser

WORKDIR /home/botuser

# Install StarCraft II
RUN wget http://blzdistsc2-a.akamaihd.net/Linux/SC2.4.10.zip && \
    unzip -P iagreetotheeula SC2.4.10.zip -d ./ && \
    rm SC2.4.10.zip

# Rename to lowercase for the python-sc2 library
RUN mv StarCraftII/Maps StarCraftII/maps

# Get the latest version of the maps from the aiarena wiki or use the provided links
ARG MAP_LINKS=https://aiarena.net/wiki/184/plugin/attachments/download/35/
RUN set -- $MAP_LINKS && \
    for LINK in "$@"; do \
        wget $LINK -O maps.zip && \
        unzip maps.zip -d ./StarCraftII/maps && \
        rm maps.zip; \
    done
