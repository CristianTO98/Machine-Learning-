import json
import os
import time
import uuid

import redis
from structlog import get_logger

from logger import init_logger

init_logger()

log = get_logger("worker")

# Get the process ID.
pid = os.getpid()

# We will generate a unique ID for this worker.
# It will be used to identify the worker in the logs.
worker_id = uuid.uuid4().hex

log = log.bind(worker_id=worker_id, worker_pid=pid)
log.info("Initializing worker")

r = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    db=int(os.environ["REDIS_DB"]),
)

# Check if connection to Redis is successful.
try:
    r.ping()
except redis.exceptions.ConnectionError:
    log.error("Cannot connect to Redis", worker_id=worker_id)
    exit(1)

log.info("Connected to Redis", worker_id=worker_id)


def handle_email(task):
    task_id = task["taskId"]
    request_id = task["requestId"]
    action = task["action"]
    if action == "itemPurchased":
        log.info(
            "Sending purchase email to %s" % task["data"]["userId"],
            request_id=request_id,
            task_id=task_id,
        )
        time.sleep(5)
        log.info(
            "Email sent to %s" % task["data"]["userId"],
            request_id=request_id,
            task_id=task_id,
        )


class GracefulKiller:
    stop = False

    def __init__(self):
        import signal
        # SIGINT is what happens when you do CTRL-C from the terminal
        signal.signal(signal.SIGINT, self.exit_gracefully)
        # SIGTERM is the default signal sent by kill
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        log.warning("Received stop signal %s" % signum)
        self.stop = True


killer = GracefulKiller()

while not killer.stop:
    message = r.lpop("default")
    if message:
        task = json.loads(message)
        task_id = task["taskId"]
        request_id = task["requestId"]
        log.debug(
            "Processing task",
            queue_name="default",
            task_id=task_id,
            request_id=request_id,
        )
        r.set("task:{}:status".format(task_id), "processing")
        r.set("task:{}:worker".format(task_id), worker_id)
        if task["type"] == "email":
            try:
                handle_email(task)
                r.set("task:{}:status".format(task_id), "done")
            except Exception as e:
                log.error(
                    "Error processing task",
                    queue_name="default",
                    task_id=task_id,
                    request_id=request_id,
                    error=str(e),
                )
                r.set("task:{}:status".format(task_id), "error")
        else:
            log.warning(
                "No handler found for type %s" % task["type"],
                queue_name="default",
                task_id=task_id,
                request_id=request_id,
            )
    else:
        time.sleep(0.1)

log.info("Worker stopped")
