import json

import redis


r = redis.Redis(
  host= 'eu1-quiet-mastodon-38700.upstash.io',
  port= 38700,
  password= '0f377379aaf44ff384de76931fc0a508',
  ssl=True
)

# Observador

pubsub = r.pubsub()
pubsub.subscribe("chat")



