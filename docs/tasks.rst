Tasks
=====
.. py:currentmodule:: django_q

.. _async:

async_task()
------------

.. warning:: Since Python 3.7 `async` became a reserved keyword and was refactored to `async_task`


Use :func:`async_task` from your code to quickly offload tasks to the :class:`Cluster`:

.. code:: python

    from django_q.tasks import async_task, result

    # create the task
    async_task('math.copysign', 2, -2)

    # or with import and storing the id
    import math.copysign

    task_id = async_task(copysign, 2, -2)

    # get the result
    task_result = result(task_id)

    # result returns None if the task has not been executed yet
    # you can wait for it
    task_result = result(task_id, 200)

    # but in most cases you will want to use a hook:

    async_task('math.modf', 2.5, hook='hooks.print_result')

    # hooks.py
    def print_result(task):
        print(task.result)

:func:`async_task` can take the following optional keyword arguments:

hook
""""
The function to call after the task has been executed. This function gets passed the complete :class:`Task` object as its argument.

group
"""""
A group label. Check :doc:`group` for group functions.

save
""""
Overrides the result backend's save setting for this task.

timeout
"""""""
Overrides the cluster's timeout setting for this task.

See :ref:`retry` for details how to set values for timeout.

ack_failure
"""""""""""
Overrides the cluster's :ref:`ack_failures` setting for this task.

sync
""""
Simulates a task execution synchronously. Useful for testing.
Can also be forced globally via the :ref:`sync` configuration option.

cached
""""""
Redirects the result to the cache backend instead of the database if set to ``True`` or to an integer indicating the cache timeout in seconds.
e.g. ``cached=60``. Especially useful with large and group operations where you don't need the all results in your
database and want to take advantage of the speed of your cache backend.

broker
""""""
A broker instance, in case you want to control your own connections.

task_name
"""""""""

Optionally overwrites the auto-generated task name.

q_options
"""""""""
None of the option keywords get passed on to the task function.
As an alternative you can also put them in
a single keyword dict named ``q_options``. This enables you to use these keywords for your function call::

    # Async options in a dict

    opts = {'hook': 'hooks.print_result',
            'group': 'math',
            'timeout': 30}

    async_task('math.modf', 2.5, q_options=opts)

Please note that this will override any other option keywords.

.. note::
    For tasks to be processed you will need to have a worker cluster running in the background using ``python manage.py qcluster``
    or you need to configure Django Q to run in synchronous mode for testing using the :ref:`sync` option.


AsyncTask
---------

Optionally you can use the :class:`AsyncTask` class to instantiate a task and keep everything in a single object.:

.. code-block:: python

    # AsyncTask class instance example
    from django_q.tasks import AsyncTask

    # instantiate an async task
    a = AsyncTask('math.floor', 1.5, group='math')

    # you can set or change keywords afterwards
    a.cached = True

    # run it
    a.run()

    # wait indefinitely for the result and print it
    print(a.result(wait=-1))

    # change the args
    a.args = (2.5,)

    # run it again
    a.run()

    # wait max 10 seconds for the result and print it

    print(a.result(wait=10))

.. code-block:: python

    1
    2

Once you change any of the parameters of the task after it has run, the result is invalidated and you will have to :func:`AsyncTask.run` it again to retrieve a new result.

Cached operations
-----------------
You can run your tasks results against the Django cache backend instead of the database backend by either using the global :ref:`cached` setting or by supplying the ``cached`` keyword to individual functions.
This can be useful if you are not interested in persistent results or if you run large group tasks where you only want the final result.
By using a cache backend like Redis or Memcached you can speed up access to your task results significantly compared to a relational database.

When you set ``cached=True``, results will be saved permanently in the cache and you will have to rely on your backend's cleanup strategies (like LRU) to
manage stale results.
You can also opt to set a manual timeout on the results, by setting e.g. ``cached=60``. Meaning the result will be evicted from the cache after 60 seconds.
This works both globally or on individual async executions.::

    # simple cached example
    from django_q.tasks import async_task, result

    # cache the result for 10 seconds
    id = async_task('math.floor', 100, cached=10)

    # wait max 50ms for the result to appear in the cache
    result(id, wait=50, cached=True)

    # or fetch the task object
    task = fetch(id, cached=True)

    # and then save it to the database
    task.save()

As you can see you can easily turn a cached result into a permanent database result by calling ``save()`` on it.

This also works for group actions::

    # cached group example
    from django_q.tasks import async_task, result_group
    from django_q.brokers import get_broker

    # set up a broker instance for better performance
    broker = get_broker()

    # Async a hundred functions under a group label
    for i in range(100):
        async_task('math.frexp',
                i,
                group='frexp',
                cached=True,
                broker=broker)

    # wait max 50ms for one hundred results to return
    result_group('frexp', wait=50, count=100, cached=True)

If you don't need hooks, that exact same result can be achieved by using the more convenient :func:`async_iter`.

Synchronous testing
-------------------

:func:`async_task` can be instructed to execute a task immediately by setting the optional keyword ``sync=True``.
The task will then be injected straight into a worker and the result saved by a monitor instance::

    from django_q.tasks import async_task, fetch

    # create a synchronous task
    task_id = async_task('my.buggy.code', sync=True)

    # the task will then be available immediately
    task = fetch(task_id)

    # and can be examined
    if not task.success:
        print('An error occurred: {}'.format(task.result))

.. code:: bash

    An error occurred: ImportError("No module named 'my'",)

Note that :func:`async_task` will block until the task is executed and saved. This feature bypasses the broker and is intended for debugging and development.
Instead of setting ``sync`` on each individual ``async_task`` you can also configure :ref:`sync` as a global override.

Connection pooling
------------------

Django Q tries to pass broker instances around its parts as much as possible to save you from running out of connections.
When you are making individual calls to :func:`async_task` a lot though, it can help to set up a broker to reuse for :func:`async_task`:

.. code:: python

    # broker connection economy example
    from django_q.tasks import async_task
    from django_q.brokers import get_broker

    broker = get_broker()
    for i in range(50):
        async_task('math.modf', 2.5, broker=broker)

.. tip::

    If you are using `django-redis <https://github.com/niwinz/django-redis>`__  and the redis broker, you can :ref:`configure <django_redis>` Django Q to use its connection pool.


Reference
---------

.. py:function:: async_task(func, *args, hook=None, group=None, timeout=None,\
    save=None, sync=False, cached=False, broker=None, q_options=None, **kwargs)

    Puts a task in the cluster queue

   :param object func: The task function to execute
   :param tuple args: The arguments for the task function
   :param object hook: Optional function to call after execution
   :param str group: An optional group identifier
   :param int timeout: Overrides global cluster :ref:`timeout`.
   :param bool save: Overrides global save setting for this task.
   :param bool ack_failure: Overrides the global :ref:`ack_failures` setting for this task.
   :param bool sync: If set to True, async_task will simulate a task execution
   :param cached: Output the result to the cache backend. Bool or timeout in seconds
   :param broker: Optional broker connection from :func:`brokers.get_broker`
   :param dict q_options: Options dict, overrides option keywords
   :param dict kwargs: Keyword arguments for the task function
   :returns: The uuid of the task
   :rtype: str

.. py:function:: result(task_id, wait=0, cached=False)

    Gets the result of a previously executed task

    :param str task_id: the uuid or name of the task
    :param int wait: optional milliseconds to wait for a result. -1 for indefinite
    :param bool cached: run this against the cache backend.
    :returns: The result of the executed task

.. py:function:: fetch(task_id, wait=0, cached=False)

    Returns a previously executed task

    :param str task_id: the uuid or name of the task
    :param int wait: optional milliseconds to wait for a result. -1 for indefinite
    :param bool cached: run this against the cache backend.
    :returns: A task object
    :rtype: Task

    .. versionchanged:: 0.2.0

    Renamed from get_task


.. py:function:: queue_size()

    Returns the size of the broker queue.
    Note that this does not count tasks currently being processed.

    :returns: The amount of task packages in the broker
    :rtype: int

.. py:function:: delete_cached(task_id, broker=None)

    Deletes a task from the cache backend

    :param str task_id: the uuid of the task
    :param broker: an optional broker instance


.. py:class:: Task

    Database model describing an executed task

    .. py:attribute:: id

    An  :func:`uuid.uuid4()` identifier

    .. py:attribute:: name

    The name of the task as a humanized version of the :attr:`id`

        .. note::

            This is for convenience and can be used as a parameter for most functions that take a `task_id`.
            Keep in mind that it is not guaranteed to be unique if you store very large amounts of tasks in the database.

    .. py:attribute:: func

    The function or reference that was executed

    .. py:attribute:: hook


    The function to call after execution.

    .. py:attribute:: args

    Positional arguments for the function.

    .. py:attribute:: kwargs


    Keyword arguments for the function.

    .. py:attribute:: result

    The result object. Contains the error if any occur.

    .. py:attribute:: started

    The moment the task was created by an async command

    .. py:attribute:: stopped

    The moment a worker finished this task

    .. py:attribute:: success

    Was the task executed without problems?

    .. py:method:: time_taken

    Calculates the difference in seconds between started and stopped.

        .. note::

            Time taken represents the time a task spends in the cluster, this includes any time it may have waited in the queue.

    .. py:method:: group_result(failures=False)

    Returns a list of results from this task's group.
    Set failures to ``True`` to include failed results.

    .. py:method:: group_count(failures=False)

    Returns a count of the number of task results in this task's group.
    Returns the number of failures when ``failures=True``

    .. py:method:: group_delete(tasks=False)

    Resets the group label on all the tasks in this task's group.
    If ``tasks=True`` it will also delete the tasks in this group from the database, including itself.

    .. py:classmethod:: get_result(task_id)

    Gets a result directly by task uuid or name.

    .. py:classmethod:: get_result_group(group_id, failures=False)

    Returns a list of results from a task group.
    Set failures to ``True`` to include failed results.

    .. py:classmethod:: get_task(task_id)

    Fetches a single task object by uuid or name.

    .. py:classmethod:: get_task_group(group_id, failures=True)

    Gets a queryset of tasks with this group id.
    Set failures to ``False`` to exclude failed tasks.

    .. py:classmethod::  get_group_count(group_id, failures=False)

    Returns a count of the number of tasks results in a group.
    Returns the number of failures when ``failures=True``

    .. py:classmethod:: delete_group(group_id, objects=False)

    Deletes a group label only, by default.
    If ``objects=True`` it will also delete the tasks in this group from the database.

.. py:class:: Success

    A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is ``True``.

.. py:class:: Failure

     A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is ``False``.


.. py:class:: AsyncTask(func, *args, **kwargs)

    A class wrapper for the :func:`async_task` function.

    :param object func: The task function to execute
    :param tuple args: The arguments for the task function
    :param dict kwargs: Keyword arguments for the task function, including async_task options

    .. py:attribute:: id

    The task unique identifier. This will only be available after it has been :meth:`run`

    .. py:attribute:: started

    Bool indicating if the task has been run with the current parameters

    .. py:attribute:: func

    The task function to execute

    .. py:attribute:: args

    A tuple of arguments for the task function

    .. py:attribute:: kwargs

    Keyword arguments for the function. Can include any of the optional async_task keyword attributes directly or in a `q_options` dictionary.

    .. py:attribute:: broker

    Optional :class:`Broker` instance to use

    .. py:attribute:: sync

    Run this task inline instead of asynchronous.

    .. py:attribute:: save

    Overrides the global save setting.

    .. py:attribute:: hook

    Optional function to call after a result is available. Takes the result :class:`Task` as the first argument.

    .. py:attribute:: group

    Optional group identifier

    .. py:attribute:: cached

    Run the task against the cache result backend.

    .. py:method:: run()

    Send the task to a worker cluster for execution

    .. py:method:: result(wait=0)

     The task result. Always returns None if the task hasn't been run with the current parameters.

        :param int wait: the number of milliseconds to wait for a result. -1 for indefinite


    .. py:method:: fetch(wait=0)

    Returns the full :class:`Task` result instance.

        :param int wait: the number of milliseconds to wait for a result. -1 for indefinite

    .. py:method:: result_group(failures=False, wait=0, count=None)

    Returns a list of results from this task's group.

        :param bool failures: set this to ``True`` to include failed results
        :param int wait: optional milliseconds to wait for a result or count. -1 for indefinite
        :param int count: block until there are this many results in the group

    .. py:method:: fetch_group(failures=True, wait=0, count=None)

    Returns a list of task results from this task's group

        :param bool failures: set this to ``False`` to exclude failed tasks
        :param int wait: optional milliseconds to wait for a task or count. -1 for indefinite
        :param int count: block until there are this many tasks in the group
