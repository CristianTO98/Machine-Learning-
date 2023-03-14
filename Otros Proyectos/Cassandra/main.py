from cassandra.cluster import Cluster

cluster = Cluster(["localhost"], port = 9042)

session = cluster.connect()


session.execute("Aqui metemios los comandos y las queries")


