FROM luguenin/starcraft2-base:python_3.11

WORKDIR /home/botuser/app
USER root

# Install Git
RUN apt-get update && apt-get install -y git

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
