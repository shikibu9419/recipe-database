import redis
import os

pool = redis.ConnectionPool(host=os.environ.get('REDIS_HOST'), port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool, decode_responses=True)
