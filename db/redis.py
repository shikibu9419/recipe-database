from redis import from_url
import os

redis = from_url(os.environ['REDIS_URL'], decode_responses=True)