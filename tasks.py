import datetime
import time
import os
from celery import Celery
import redis
from redis_instance import r

celery_app = Celery('hello', broker=os.environ['REDIS_URL'])


@celery_app.task
def hello(task_id):
    r.hset(task_id, 'status', 'running')
    time.sleep(120)
    r.hset(task_id, 'status', 'complete')
