FROM starcraft2-base

WORKDIR /home/botuser/app

# Copy only requirements to cache them in docker layer
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Change ownership to allow development in container
USER root
RUN chown -R botuser:botuser .
USER botuser

# Copy maps from host to container if provided as bind mount
CMD if [ -d "/host_maps" ]; \
  then cp -R /host_maps/* /home/botuser/StarCraftII/Maps/; \
fi && \
/bin/bash
