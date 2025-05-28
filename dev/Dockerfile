# docker/dev/Dockerfile

# ─── 1) Base image & tools ─────────────────────────────────────────────────────
FROM ubuntu:22.04

ENV HISTFILE=/home/user/.bash_history \
    HISTCONTROL=ignoreboth \
    HISTSIZE=1000 \
    HISTFILESIZE=2000 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC

# install Python 3.12 and make
RUN apt-get update && apt-get install -y \
      bash \
      software-properties-common \
      curl \
      gnupg \
      make \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
      python3.12 \
      python3.12-venv \
      python3.12-dev \
    && ln -sf /usr/bin/python3.12 /usr/bin/python3 \
    && ln -sf /usr/bin/python3.12 /usr/bin/python \
    && curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 \
    && rm -rf /var/lib/apt/lists/*

# ─── 2) Install packaging helpers as root (so pipreqs ends up in /usr/local/bin) ─
RUN python -m pip install --upgrade pip \
 && python -m pip install pipreqs tomlkit build setuptools wheel

# ─── 3) Create non‑root user & persistent bash history ─────────────────────────
RUN useradd -m -s /bin/bash user \
 && touch /home/user/.bash_history \
 && chown user:user /home/user/.bash_history \
 && chmod 600 /home/user/.bash_history \
 && echo 'PROMPT_COMMAND="history -a; history -w; $PROMPT_COMMAND"' \
       >> /home/user/.bashrc

# ─── 4) Entrypoint ──────────────────────────────────────────────────────────────
#COPY docker/dev/entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh

# expose nsflow client port and neuro-san server port
EXPOSE 4173
EXPOSE 30013

USER user
WORKDIR /home/user/app