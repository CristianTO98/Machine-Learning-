import time
import uuid
from threading import Thread

import docker
import redis
from docker.errors import NotFound
from structlog import get_logger

from logger import init_logger

init_logger()

log = get_logger("autoscale")

client = docker.from_env()

r = redis.Redis()

# Check if connection to Redis is successful.
try:
    r.ping()
except redis.exceptions.ConnectionError:
    log.error("Cannot connect to Redis")
    exit(1)

log.info("Connected to Redis")

# We use a set to keep track of running containers in the machine.
containers = set()


def is_alive(container_name):
    try:
        container = client.containers.get(container_name)
    except NotFound:
        return False
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == "running"


# We also keep track of the names of the containers we create in Redis, so we can
# recover from a crash if the process is killed or restarted.
for container_name in r.lrange('containers', 0, -1):
    # We check if the container is still alive, in which case we add it to the set.
    if is_alive(container_name.decode()):
        containers.add(container_name.decode())


def keep_alive():
    while True:
        # Check if the containers are still alive. If not, we remove them from
        # the set and from Redis. Note that we are iterating over a copy of the
        # set, so we can remove elements from the original set without problems.
        for container_name in containers.copy():
            if not is_alive(container_name):
                log.info("Container %s is not running, cleaning" % container_name)
                containers.discard(container_name)
                r.lrem('containers', 0, container_name)
        time.sleep(5.0)


t = Thread(target=keep_alive)
t.start()

# Reconciliation loop ensures that we have the right number of workers.
while True:
    # Get length of list 'default'.
    pending_tasks = r.llen("default")

    log.info("Scheduling pending tasks", pending_tasks=pending_tasks, workers=len(containers))

    # If there are more than 50 pending tasks, scale up to 5 workers.
    if pending_tasks > 50:
        desired = 5
    # Scale up to 3 workers if pending tasks is between 5 and 50.
    elif 5 < pending_tasks <= 50:
        desired = 3
    # Scale down to 1 worker if pending tasks is less than 5.
    elif 0 < pending_tasks <= 5:
        desired = 1
    else:
        desired = 0

    # Compare desired number of workers with current number of workers
    # and start or stop workers as needed.
    if desired != len(containers):
        log.info("Auto-scaling", pending_tasks=pending_tasks, desired=desired, workers=len(containers))
        if desired > len(containers):
            for _ in range(desired - len(containers)):
                log.info("Starting new worker")
                container_name = "worker-{}".format(uuid.uuid4().hex)
                client.containers.run("autoscale/worker:0.0.1",
                                      detach=True,
                                      name=container_name,
                                      network="autoscale-net",
                                      environment={"REDIS_HOST": "redis", "REDIS_PORT": "6379", "REDIS_DB": "0"})
                containers.add(container_name)
                r.rpush("containers", container_name)
        else:
            for _ in range(len(containers) - desired):
                try:
                    container_name = containers.pop()
                except KeyError:
                    continue
                else:
                    log.info("Stopping worker", worker=container_name)
                    if is_alive(container_name):
                        client.containers.get(container_name).stop()
                    r.lrem('containers', 0, container_name)
    else:
        time.sleep(0.1)
