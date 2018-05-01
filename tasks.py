import datetime
import time
import os

from celery import Celery


celery_app = Celery('hello', broker=os.environ['REDIS_URL'])


@celery_app.task
def hello():
    time.sleep(10)
    with open ('worker.txt', 'a') as hellofile:
        hellofile.write('Worker Process {}\n'.format(datetime.datetime.now()))
