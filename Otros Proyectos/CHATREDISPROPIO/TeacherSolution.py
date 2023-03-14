import json
import time

import redis

r = redis.Redis( host= 'eu1-quiet-mastodon-38700.upstash.io',
  port= 38700,
  password= '0f377379aaf44ff384de76931fc0a508',
  ssl=True)

ch = r.pubsub()

# Ask nickname for current session.
nickname = input("Enter nickname: ")


def event_handler(message):
    """
    Read incoming chatroom message.
    """
    data = message["data"]
    # Data is always serialized, we need to deserialize it.
    payload = json.loads(data)
    event = payload["event"]
    user = payload["user"]
    if event == "connected":
        print(user + " has joined!", end="\n")
    elif event == "incoming":
        msg = payload["msg"]
        print(user + " says: " + msg, end="\n")


# Subscribe to channel using callback function.
ch.psubscribe(**{"classroom": event_handler})
ch.run_in_thread(sleep_time=.01)

# Fire login event.
r.publish("classroom", json.dumps({"event": "connected", "user": nickname}))

while True:
    print()
    msg = input()
    r.publish("classroom", json.dumps({"event": "incoming", "user": nickname, "msg": msg}))
    time.sleep(0.1)
