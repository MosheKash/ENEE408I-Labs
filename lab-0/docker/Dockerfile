FROM continuumio/miniconda3:26.5.3

SHELL ["/bin/bash", "-c"]

WORKDIR ${HOME}

ENV DEBIAN_FRONTEND=noninteractive

# Basic setup
RUN apt-get update && apt-get install -y --no-install-recommends --allow-unauthenticated \
    autoconf \
    automake \
    bash-completion \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    g++ \
    git \
    iproute2 \
    iputils-ping \
    libxext-dev \
    libx11-dev \
    make \
    mc \
    mesa-utils \
    nano \
    vim \
    tree \
    pkg-config \
    sudo \
    tmux \
    tzdata \
    xclip \
    x11proto-gl-dev && \
    rm -rf /var/lib/apt/lists/*

# Set datetime and timezone correctly
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo '$TZ' | sudo tee -a /etc/timezone

ENV DEBIAN_FRONTEND=dialog

# Setup conda env

# defaults
ARG userid=1002
ARG groupid=1002

RUN groupadd -g ${groupid} -o robot
RUN useradd -ms /bin/bash --uid ${userid} -g ${groupid} robot
USER robot
WORKDIR /home/robot
RUN mkdir Desktop

COPY config/environment.yml /tmp/environment.yml

RUN conda env create -f /tmp/environment.yml
RUN echo "source activate lab-0" >> ~/.bashrc
ENV PATH /opt/conda/envs/lab-0/bin:$PATH

RUN mkdir -p lab-0/src

# Setup tmux config
ADD --chown=robot:robot https://raw.githubusercontent.com/MarylandRoboticsCenter/someConfigs/refs/heads/master/.tmux_K.conf /home/robot/.tmux.conf

ENTRYPOINT ["/bin/bash", "-i"]