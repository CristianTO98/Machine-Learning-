import redis
import json

r = redis.Redis()
print(r.ping())
user = {"nombre":"antonio"}
r.set("clave", json.dumps(user))

value = r.get("clave")
print(json.loads(value))

r.expire("clave", 10)  # TTL time-to-live

# python -m pip install redis
