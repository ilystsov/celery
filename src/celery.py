# celery.py
import os
from time import sleep

from celery import Celery
from celery.signals import task_postrun

from .db import insert_task

celery = Celery('src')

celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")


@celery.task
def user_task(should_fail: bool):
    """
    Simulate a time-intensive operation.
    An error occurres if should_fail is True.
    """
    sleep(7)
    if should_fail:
        raise ValueError("An error occurred in user_task")
    return True


@task_postrun.connect(sender=user_task)
def task_postrun_handler(sender, task_id, task, args, kwargs, retval, state, **kw) -> None:
    """
    The handler is triggered after a task has been executed.

    :param sender: the task class.
    :param task_id: the identifier of the task.
    :param task: the task instance.
    :param args: the arguments of the task.
    :param kwargs: the named arguments of the task.
    :param retval: the return value of the task or an exception if the task ended with an error.
    :param state: the completion state of the task ('SUCCESS', 'FAILURE').
    """
    if state == 'SUCCESS':
        result = retval
    else:
        result = str(retval)
    insert_task(task_id, result, state)