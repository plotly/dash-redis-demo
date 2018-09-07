import datetime
import time
import os
from celery import Celery
import redis
from redis_instance import r
import traceback

celery_app = Celery('hello', broker=os.environ['REDIS_URL'])


@celery_app.task
def long_running_task(task_id):
    r.zadd('tasks', int(time.time()), task_id)
    r.hset(task_id, 'status', 'Started at {}'.format(datetime.datetime.now()))
    try:
        # place your long running task code here
        # this sleep call is just to simulate a long running task
        # you can remove it once you put your code here
        time.sleep(20)
        r.hset(task_id, 'status', 'Finished at {}'.format(datetime.datetime.now()))
    except Exception as e:
        traceback.print_exc()
        r.hset(task_id, 'status', 'Error: {}'.format(e))


@celery_app.task
def error_task(task_id):
    r.zadd('tasks', int(time.time()), task_id)
    r.hset(task_id, 'status', 'Started at {}'.format(datetime.datetime.now()))
    try:
        # place your long running task code here
        # this sleep call is just to simulate a long running task
        # you can remove it once you put your code here
        time.sleep(20)
        a = 5/0
        r.hset(task_id, 'status', 'Finished at {}'.format(datetime.datetime.now()))
    except Exception as e:
        traceback.print_exc()
        r.hset(task_id, 'status', 'Error: {}'.format(e))
