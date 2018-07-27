import redis
import os
r = redis.StrictRedis.from_url(os.environ['REDIS_URL'])
