# PSL
import time
# Third Party
from django import http, urls
from django_q import tasks


def task(test_arg):
    print('Task starting.')
    time.sleep(5)
    print('Task complete! {}'.format(test_arg))
    return 'task-return'


def add_async_task(request):
    print('Adding async task')
    task_id = tasks.async_task(task, 'test-arg')
    return http.HttpResponse(
        'Added async task with <a href="{}">id</a>'.format(
            urls.reverse('get_async_task_result', args=(task_id,))
        )
    )


def get_async_task_result(request, task_id):
    print('Fetching async task result')
    task = tasks.fetch(task_id)
    if not task:
        msg = 'Task running, please wait and refresh'
    else:
        msg = 'Async task result: {}'.format(task.result)
    return http.HttpResponse(msg)


def run_task(request):
    print('Running task')
    ret = task('test-arg2')
    return http.HttpResponse('Ran task result: {}'.format(ret))
