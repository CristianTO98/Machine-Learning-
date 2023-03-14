# Autoscale task queue

This project contains a simple task queue that supports autoscaling.

## Prerequisites

* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)

## Setup

Configure a [bridge network](https://docs.docker.com/network/network-tutorial-standalone/#use-user-defined-bridge-networks) for the containers to communicate with `redis`:

```shell
$ docker network create --driver bridge autoscale-net
$ docker run -d --name redis -p 6379:6379 --network autoscale-net redis
```

Build the worker image:

```shell
$ docker build -t autoscale/worker:0.0.1 .
```

## Run

Run the autoscaler using Python:

```shell
$ python autoscale.py
```
