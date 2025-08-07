# Use an official Python runtime as a parent image
FROM node:18-slim AS frontend
WORKDIR /app
COPY apps/legal_discovery/package*.json apps/legal_discovery/
RUN npm --prefix apps/legal_discovery install
COPY apps/legal_discovery apps/legal_discovery
RUN npm --prefix apps/legal_discovery run build --silent

FROM python:3.12-slim
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential graphviz libgraphviz-dev && rm -rf /var/lib/apt/lists/*
COPY apps/legal_discovery/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && python -m spacy download en_core_web_sm
RUN pip install more_itertools

COPY . .
COPY --from=frontend /app/apps/legal_discovery/static apps/legal_discovery/static
RUN rm -rf apps/legal_discovery/node_modules

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Set default registry paths for the agent network
ENV AGENT_MANIFEST_FILE=/usr/src/app/registries/manifest.hocon
ENV AGENT_LLM_INFO_FILE=/usr/src/app/registries/llm_config.hocon

# Run the Flask application via gunicorn with eventlet for SocketIO support
# Using "python -m" avoids PATH issues on Windows hosts
CMD ["python", "-m", "gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5001", "apps.legal_discovery.interface_flask:app"]
