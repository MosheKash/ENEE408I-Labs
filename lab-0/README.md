# ENEE 467 Fall 2026: Robotics Project Laboratory
## Lab 0: Introduction to Linux Operating Systems and Python Programming

This repository contains a Docker container for the first lab as well as the necessary code templates for completing the exercises.

## Overview

Being well versed in Linux-based operating systems and Python programming is crucial for working in the field of robotics. A majority of the open-source robotics community relies on [Robot Operating System](https://www.ros.org/) (ROS) for the execution, development, and distribution of their projects. ROS runs natively on [Ubuntu](https://ubuntu.com/), and heavy emphasis is placed on working with ROS in later labs. Additionally, many open-source robotics tools are packaged with a Python API, allowing for general and accessible use. Therefore this lab is designed to give you the necessary knowledge required to comfortably work with Python and Linux-based operating systems.

To avoid software conflicts and increase portability, all lab software will be packaged as a Docker container. Follow the instructions below to get started.

## Building the Container

First check to see if the image is prebuilt on the lab computer by running the following command
```
docker image ls
```
If you see the image named `lab-0-image` in the list then you can skip the build process.

To build the Docker container, ensure that you have [Docker](https://www.docker.com/get-started/) installed and the Docker daemon running.
* Clone this repository and navigate to the `docker` folder
    ```
    cd ~/Labs
    git clone https://github.com/ENEE467-F2026/lab-0.git
    cd lab-0/docker
    ```
* Build the image with Docker compose
    ```
    userid=$(id -u) groupid=$(id -g) docker compose -f lab-0-compose.yml build
    ```

## Starting the Container

The lab computers contain a prebuild image so you will not have to build the image.
* Clone this repo to get the lab-0 code if you haven't done so already
    ```
    cd ~/Labs
    git clone https://github.com/ENEE467-F2026/lab-0.git
    cd lab-0/docker
    ```
* Run the Docker container
    ```
    docker compose -f lab-0-compose.yml run --rm lab-0-docker
    ```
* Once inside the container, you should be greeted with the following prompt indicating that the container is running
    ```
    (lab-0) robot@desktop:~$
    ```
* Edit the lab-0 code `matrix.py` and `pendulum.py` from a VS Code editor on the host machine. The repo directory `lab-0/src`  is mounted to the docker container located at `/home/robot/lab-0/src` so all changes will be reflected inside the container.
* To execute the Python script, use the following command
    ```
    cd ~/lab-0/src
    python pendulum.py
    ```

## Lab Instructions

Please follow the [lab manual](Lab_0_Python_and_Linux.pdf) closely. All instructions are contained inside the lab manual.