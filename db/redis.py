import redis
import os

pool = redis.ConnectionPool(host='redis', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool, decode_responses=True)
