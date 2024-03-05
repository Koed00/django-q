Signals
=======
.. py:currentmodule:: django_q

Available signals
-----------------

Django Q2 emits the following signals during its lifecycle.

Before enqueuing a task
"""""""""""""""""""""""

The ``django_q.signals.pre_enqueue`` signal is emitted before a task is
enqueued. The task dictionary is given as the ``task`` argument.

After spawning a worker process
"""""""""""""""""""""""""""""""

The ``django_q.signals.post_spawn`` signal is emitted after a worker process has
spawned. The process name is given as the ``proc_name`` argument (string).

Before executing a task
"""""""""""""""""""""""

The ``django_q.signals.pre_execute`` signal is emitted before a task is
executed by a worker. This signal provides two arguments:

- ``task``: the task dictionary.
- ``func``: the actual function that will be executed. If the task was created
  with a function path, this argument will be the callable function
  nonetheless.

After executing a task
""""""""""""""""""""""
The ``django_q.signals.post_execute`` signal is emitted after a task is
executed by a worker and processed by the monitor. It included the ``task`` dictionary with the result.


Subscribing to a signal
-----------------------

Connecting to a Django Q2 signal is done the same as any other Django
signal::

    from django.dispatch import receiver
    from django_q.signals import pre_enqueue, pre_execute, post_execute, post_spawn

    @receiver(pre_enqueue)
    def my_pre_enqueue_callback(sender, task, **kwargs):
        print(f"Task {task['name']} will be queued")

    @receiver(pre_execute)
    def my_pre_execute_callback(sender, func, task, **kwargs):
        print(f"Task {task['name']} will be executed by calling {func}")

    @receiver(post_execute)
    def my_post_execute_callback(sender, task, **kwargs):
        print(f"Task {task['name']} was executed with result {task['result']}")

    @receiver(post_spawn)
    def my_post_spawn_callback(sender, proc_name, **kwargs):
        print(f"Process {proc_name} has spawned")


