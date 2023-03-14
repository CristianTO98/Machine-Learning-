import json
import os
import time
import uuid
import redis
from structlog import get_logger
from logger import init_logger
from utils import GracefulKiller

init_logger()


class Worker:
    def __init__(self, auto_conect=False):
        # We will generate a unique ID for this worker.
        # It will be used to identify the worker in the logs.
        self.worker_id = uuid.uuid4().hex
        self.graceful_killer = GracefulKiller()
        self.log = get_logger("worker")
        self.log = self.log.bind(worker_id=self.worker_id)
        self.log.info("Initializing worker")
        self.r = None
        if auto_conect:
            self.connect()

    def connect(self):
        self.r = redis.Redis(host=os.environ["REDIS_HOST"], port=int(os.environ["REDIS_PORT"]))
        # Check if connection to Redis is successful.
        try:
            self.r.ping()
        except redis.exceptions.ConnectionError:
            self.log.error("Cannot connect to Redis", worker_id=self.worker_id)
            self.log.info("Connected to Redis", worker_id=self.worker_id)
            exit(1)

    def _handle_email(self, task):
        task_id = task["taskId"]
        request_id = task["requestId"]
        action = task["action"]
        if action == "itemPurchased":
            self.log.info(
                "Sending purchase email to %s" % task["data"]["to"],
                request_id=request_id,
                task_id=task_id,
            )
            time.sleep(0.1)
            self.log.info(
                "Email sent to %s" % task["data"]["to"],
                request_id=request_id,
                task_id=task_id,
            )

    def start(self):
        while not self.graceful_killer.kill_now:
            message = self.r.lpop("default")
            if message:
                task = json.loads(message)
                task_id = task["taskId"]
                request_id = task["requestId"]
                self.log.debug(
                    "Processing task",
                    queue_name="default",
                    task_id=task_id,
                    request_id=request_id,
                )
                self.r.set("task:{}:status".format(task_id), "processing")
                self.r.set("task:{}:worker".format(task_id), self.worker_id)
                if task["type"] == "email":
                    try:
                        self._handle_email(task)
                        self.r.set("task:{}:status".format(task_id), "done")
                    except Exception as e:
                        self.log.error(
                            "Error processing task",
                            queue_name="default",
                            task_id=task_id,
                            request_id=request_id,
                            error=str(e),
                        )
                        self.r.set("task:{}:status".format(task_id), "error")
                else:
                    self.log.warning(
                        "No handler found for type %s" % task["type"],
                        queue_name="default",
                        task_id=task_id,
                        request_id=request_id,
                    )
            time.sleep(0.01)

        self.log.info("End of worker.")


if __name__ == "__main__":
    worker = Worker(auto_conect=True)
    worker.start()
