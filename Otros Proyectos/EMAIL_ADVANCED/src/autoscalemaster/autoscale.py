import time
import uuid
import docker
import redis
from structlog import get_logger
from logger import init_logger

init_logger()


class AutoScale:
    def __init__(self, auto_connect=False):
        self.client = docker.from_env()
        self.log = get_logger("autoscale")
        self.r = None
        if auto_connect:
            self.connect()

    def connect(self):
        self.r = redis.Redis()

        # Check if connection to Redis is successful.
        try:
            self.r.ping()
        except redis.exceptions.ConnectionError:
            self.log.error("Cannot connect to Redis")
            exit(1)

        self.log.info("Connected to Redis")

    def start(self):
        workers = set()

        self.log.info("Starting reconciliation loop")

        # Reconciliation loop to ensure we have the right number of workers.
        while True:
            # Get length of list 'default'.
            pending_tasks = self.r.llen("default")

            self.log.info("Scheduling pending tasks", pending_tasks=pending_tasks, workers=len(workers))

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
            if desired != len(workers):
                self.log.info("Auto-scaling", pending_tasks=pending_tasks, desired=desired, workers=len(workers))
                if desired > len(workers):
                    for i in range(desired - len(workers)):
                        self.log.info("Starting new worker")
                        cid = f"worker-{uuid.uuid4().hex}"
                        # p = subprocess.Popen(["C:/Users/Zaloon098/RedisCon/Scripts/python.exe", "worker.py"],
                        #                     stdout=subprocess.DEVNULL)

                        self.client.containers.run("app/worker:0.1.0", detach=True, network="emailservice", name=cid,
                                                   enviroment={
                                                       "REDIS_HOST": "email_redis",
                                                       "REDIS_PORT": "6379",
                                                       "LOGTAIL_KEY": "1LbjFUTmk7qFs7P1d1U1SZW4"
                                                   })
                        workers.add(cid)
                else:
                    for i in range(len(workers) - desired):
                        cid = workers.pop()
                        # p.terminate()
                        try:
                            self.client.containers.get(cid).stop()
                        except Exception:
                            pass

            time.sleep(1.0)  # Reconcile interval.


if __name__ == "__main__":
    autosc = AutoScale(auto_connect=True)
    autosc.start()
