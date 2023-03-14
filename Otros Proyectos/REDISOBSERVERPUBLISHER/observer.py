import redis

# REFACTORIN GURU BUENA PAGINA PARA VER SOLUCIONES COMO POR EJEM EL SINGLENTON

r = redis.Redis(
  host= 'eu1-quiet-mastodon-38700.upstash.io',
  port= 38700,
  password= '0f377379aaf44ff384de76931fc0a508',
  ssl=True
)

ch = r.pubsub()

ch.subscribe("mi-canal")

while True:
    message = ch.get_message()
    if message:
        print(message)
time.sleep(0.001)

