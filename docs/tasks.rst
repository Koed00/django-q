Tasks
=====
.. py:currentmodule:: django_q

Async
-----

Use :func:`async` from your code to quickly offload tasks to the :class:`Cluster`:

.. code:: python

    from django_q import async, result

    # create the task
    async('math.copysign', 2, -2)

    # or with import and storing the id
    import math.copysign

    task_id = async(copysign, 2, -2)

    # get the result
    task_result = result(task_id)

    # result returns None if the task has not been executed yet
    # so in most cases you will want to use a hook:

    async('math.modf', 2.5, hook='hooks.print_result')

    # hooks.py
    def print_result(task):
        print(task.result)

Groups
------
You can group together results by passing :func:`async` the optional `group` keyword:

.. code-block:: python

    # result group example
    from django_q import async, result_group

    for i in range(4):
        async('math.modf', i, group='modf')

    # after the tasks have finished you can get the group results
    result = result_group('modf')
    print(result)

.. code-block:: python

    [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0), (0.0, 3.0)]

Take care to not limit your results database too much and call :func:`delete_group` before each run, unless you want your results to keep adding up.
Instead of :func:`result_group` you can also use :func:`fetch_group` to return a queryset of :class:`Task` objects.:

.. code-block:: python

    # fetch group example
    from django_q import fetch_group, count_group, result_group

    # count the number of failures
    failure_count = count_group('modf', failures=True)

    # only use the successes
    results = fetch_group('modf')
    if failure_count:
        results.exclude(success=False)
    results =  [task.result for task in successes]

    # this is the same as
    results = fetch_group('modf', failures=False)
    results =  [task.result for task in successes]

    # and the same as
    results = result_group('modf') # filters failures by default


Getting results by using :func:`result_group` is of course much faster than using :func:`fetch_group`, but it doesn't offer the benefits of Django's queryset functions.

.. note::

   Although :func:`fetch_group` returns a queryset, due to the nature of the PickleField , calling `Queryset.values` on it will return a list of encoded results.
   Use list comprehension or an iterator instead.

Synchronous testing
-------------------

:func:`async` can be instructed to execute a task immediately by setting the optional keyword `sync=True`.
The task will then be injected straight into a worker and the result saved by a monitor instance::

    from django_q import async, fetch

    # create a synchronous task
    task_id = async('my.buggy.code', sync=True)

    # the task will then be available immediately
    task = fetch(task_id)

    # and can be examined
    if not task.success:
        print('An error occurred: {}'.format(task.result))

.. code:: bash

    An error occurred: ImportError("No module named 'my'",)

Note that :func:`async` will block until the task is executed and saved. This feature bypasses the Redis server and is intended for debugging and development.

Connection pooling
------------------

Django Q tries to pass redis connections around its parts as much as possible to save you from running out of connections.
When you are making individual calls to :func:`async` a lot though, it can help to set up a redis connection to pass to :func:`async`:

.. code:: python

    # redis connection economy example
    from django_q import async
    from django_q.conf import redis_client

    for i in range(50):
        async('math.modf', 2.5, redis=redis_client)

.. tip::

    If you are using `django-redis <https://github.com/niwinz/django-redis>`__ , you can :ref:`configure <django_redis>` Django Q to use its connection pool.


Reference
---------

.. py:function:: async(func, *args, hook=None, group=None, timeout=None,\
    sync=False, redis=None, **kwargs)

    Puts a task in the cluster queue

   :param object func: The task function to execute
   :param tuple args: The arguments for the task function
   :param object hook: Optional function to call after execution
   :param str group: An optional group identifier
   :param int timeout: Overrides global cluster :ref:`timeout`.
   :param bool sync: If set to True, async will simulate a task execution
   :param redis: Optional redis connection
   :param dict kwargs: Keyword arguments for the task function
   :returns: The uuid of the task
   :rtype: str

.. py:function:: result(task_id)

    Gets the result of a previously executed task

    :param str task_id: the uuid or name of the task
    :returns: The result of the executed task

.. py:function:: fetch(task_id)

    Returns a previously executed task

    :param str name: the uuid or name of the task
    :returns: The task if any
    :rtype: Task

    .. versionchanged:: 0.2.0

    Renamed from get_task

.. py:function:: result_group(group_id, failures=False)

    Returns the results of a task group

    :param str group_id: the group identifier
    :param bool failures: set this to `True` to include failed results
    :returns: a list of results
    :rtype: list

.. py:function:: fetch_group(group_id, failures=True)

    Returns a list of tasks in a group

    :param str group_id: the group identifier
    :param bool failures: set this to `False` to exclude failed tasks
    :returns: a list of Tasks
    :rtype: list

.. py:function:: count_group(group_id, failures=False)

    Counts the number of task results in a group.

    :param str group_id: the group identifier
    :param bool failures: counts the number of failures if `True`
    :returns: the number of tasks or failures in a group
    :rtype: int

.. py:function:: delete_group(group_id, tasks=False)

    Deletes a group label from the database.

    :param str group_id: the group identifier
    :param bool tasks: also deletes the associated tasks if `True`
    :returns: the numbers of tasks affected
    :rtype: int

.. py:class:: Task

    Database model describing an executed task

    .. py:attribute:: id

    An  :func:`uuid.uuid4()` identifier

    .. py:attribute:: name

    The name of the task as a humanized version of the :attr:`id`

        .. note::

            This is for convenience and can be used as a parameter for most functions that take a `task_id`.
            Keep in mind however that it is not guaranteed to be unique if you store very large amounts of tasks in the database.

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

    .. py:classmethod:: get_result(task_id)

    Gets a result directly by task uuid or name.

    .. py:classmethod:: get_result_group(group_id, failures=False)

    Returns a list of results from a task group.
    Set failures to `True` to include failed results.

    .. py:classmethod:: get_task(task_id)

    Fetches a single task object by uuid or name.

    .. py:classmethod:: get_task_group(group_id, failures=True)

    Gets a queryset of tasks with this group id.
    Set failures to `False` to exclude failed tasks.

    .. py:classmethod::  get_group_count(group_id, failures=False)

    Returns a count of the number of tasks results in a group.
    Returns the number of failures when `failures=True`

    .. py:classmethod:: delete_group(group_id, objects=False)

    Deletes a group label only, by default.
    If `objects=True` it will also delete the tasks in this group from the database.

.. py:class:: Success

    A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is True.

.. py:class:: Failure

     A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is False.