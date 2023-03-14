import json
import uuid

import redis
from structlog import get_logger

from src.autoscalemaster.logger import init_logger

init_logger()

log = get_logger("app")

r = redis.Redis()

# Check if connection to Redis is successful.
try:
    r.ping()
except redis.exceptions.ConnectionError:
    log.error("Cannot connect to Redis")
    exit(1)

log.info("Connected to Redis")


def get_task():
    return {
        # This UUID simulates the user/service that submitted the task.
        "requestId": uuid.uuid4().hex,
        # Unique ID for this task.
        "taskId": uuid.uuid4().hex,
        # Which service is responsible to handle this task.
        "type": "email",
        # Action needed to be performed by the service (either "userRegistered" or "itemPurchased").
        "action": "itemPurchased",
        # Status of the task.
        "status": "pending",
        # Data needed to perform the action. Depends on the action type.
        "data": {
            "userId": uuid.uuid4().hex,
            "itemId": uuid.uuid4().hex,
            "quantity": 1,
            "purchasedAt": "2020-01-01T00:00:00Z",
        },
    }


for i in range(20):
    task = get_task()

    log.debug(
        "Submitting task",
        request_id=task["requestId"],
        task_id=task["taskId"],
        queue_name="default",
    )

    r.rpush("default", json.dumps(task))

    log.debug(
        "Task submitted to queue",
        request_id=task["requestId"],
        task_id=task["taskId"],
        queue_name="default",
    )

    r.set("task:{}".format(task["taskId"]), json.dumps(task))
    r.set("task:{}:status".format(task["taskId"]), task["status"])
