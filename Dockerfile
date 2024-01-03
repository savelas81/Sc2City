FROM starcraft2-base

WORKDIR /home/botuser/app
USER root

# Copy only requirements to cache them in docker layer
RUN pip install poetry
COPY pyproject.toml poetry.lock ./

# Avoid using virtualenv in docker
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

COPY . .

# Change ownership to allow development in container
RUN chown -R botuser:botuser .
USER botuser

# Copy maps from host to container if provided as bind mount
CMD if [ -d "/host_maps" ]; then \
    cp -R /host_maps/* /home/botuser/StarCraftII/maps/; \
  fi && \
  /bin/bash
