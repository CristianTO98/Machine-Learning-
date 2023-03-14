import redis

# REFACTORIN GURU BUENA PAGINA PARA VER SOLUCIONES COMO POR EJEM EL SINGLENTON

r = redis.Redis(
  host= 'eu1-quiet-mastodon-38700.upstash.io',
  port= 38700,
  password= '0f377379aaf44ff384de76931fc0a508',
  ssl=True
)

r.set('foo','bar')
print(r.get('foo'))

class RedisClient:
  client = None

  def __new__(cls):
    if cls.client is None:
      print("conecting to Reddis db")
      cls.client = redis.Redis()
    return cls.client

# Singlenton
client = RedisClient()
client_two = RedisClient()
client_three = RedisClient()
client_four = RedisClient()


