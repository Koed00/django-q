Tasks
=====
.. py:currentmodule:: django_q

.. _async:

Async
-----

Use :func:`async` from your code to quickly offload tasks to the :class:`Cluster`:

.. code:: python

    from django_q.tasks import async, result

    # create the task
    async('math.copysign', 2, -2)

    # or with import and storing the id
    import math.copysign

    task_id = async(copysign, 2, -2)

    # get the result
    task_result = result(task_id)

    # result returns None if the task has not been executed yet
    # you can wait for it
    task_result = result(task_id, 200)

    # but in most cases you will want to use a hook:

    async('math.modf', 2.5, hook='hooks.print_result')

    # hooks.py
    def print_result(task):
        print(task.result)

:func:`async` can take the following optional keyword arguments:

hook
""""
The function to call after the task has been executed. This function gets passed the complete :class:`Task` object as its argument.

group
"""""
A group label. Check :ref:`groups` for group functions.

save
""""
Overrides the result backend's save setting for this task.

timeout
"""""""
Overrides the cluster's timeout setting for this task.

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

q_options
"""""""""
None of the option keywords get passed on to the task function.
As an alternative you can also put them in
a single keyword dict named ``q_options``. This enables you to use these keywords for your function call::

    # Async options in a dict

    opts = {'hook': 'hooks.print_result',
            'group': 'math',
            'timeout': 30}

    async('math.modf', 2.5, q_options=opts)

Please not that this will override any other option keywords.

.. note::
    For tasks to be processed you will need to have a worker cluster running in the background using ``python manage.py qcluster``
    or you need to configure Django Q to run in synchronous mode for testing using the :ref:`sync` option.



Async Iterable
--------------
If you have an iterable object with arguments for a function, you can use :func:`async_iter` to async them with a single command::

    # Async Iterable example
    from django_q.tasks import async_iter, result

    # set up a list of arguments for math.floor
    iter = [i for i in range(100)]

    # async iter them
    id=async_iter('math.floor',iter)

    # wait for the collated result for 1 second
    result_list = result(id, wait=1000)

This will individually queue 100 tasks to the worker cluster, which will save their results in the cache backend for speed.
Once all the 100 results are in the cache, they are collated into a list and saved as a single result in the database. The cache results are then cleared.
Needs the Django cache framework.

.. _groups:

Groups
------
You can group together results by passing :func:`async` the optional ``group`` keyword:

.. code-block:: python

    # result group example
    from django_q.tasks import async, result_group

    for i in range(4):
        async('math.modf', i, group='modf')

    # wait until the group has 4 results
    result = result_group('modf', count=4)
    print(result)

.. code-block:: python

    [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0), (0.0, 3.0)]

Note that the same can be achieved much faster with :func:`async_iter`

Take care to not limit your results database too much and call :func:`delete_group` before each run, unless you want your results to keep adding up.
Instead of :func:`result_group` you can also use :func:`fetch_group` to return a queryset of :class:`Task` objects.:

.. code-block:: python

    # fetch group example
    from django_q.tasks import fetch_group, count_group, result_group

    # count the number of failures
    failure_count = count_group('modf', failures=True)

    # only use the successes
    results = fetch_group('modf')
    if failure_count:
        results = results.exclude(success=False)
    results =  [task.result for task in successes]

    # this is the same as
    results = fetch_group('modf', failures=False)
    results =  [task.result for task in successes]

    # and the same as
    results = result_group('modf') # filters failures by default


Getting results by using :func:`result_group` is of course much faster than using :func:`fetch_group`, but it doesn't offer the benefits of Django's queryset functions.

.. note::

   Calling ``Queryset.values`` for the result on Django 1.7 or lower will return a list of encoded results.
   If you can't upgrade to Django 1.8, use list comprehension or an iterator to return decoded results.

You can also access group functions from a task result instance:

.. code-block:: python

    from django_q.tasks import fetch

    task = fetch('winter-speaker-alpha-ceiling')
    if  task.group_count() > 100:
        print(task.group_result())
        task.group_delete()
        print('Deleted group {}'.format(task.group))

Cached operations
-----------------
You can run your tasks results against the Django cache backend instead of the database backend by either using the global :ref:`cached` setting or by supplying the ``cached`` keyword to individual functions.
This can be useful if you are not interested in persistent results or if you run large group tasks where you only want the final result.
By using a cache backend like Redis or Memcached you can speed up access to your task results significantly compared to a relational database.

When you set ``cached=True``, results will be saved permanently in the cache and you will have to rely on your backend's cleanup strategies (like LRU) to
manage stale results.
You can also opt to set a manual timeout on the results, by setting ``cached=60``. Meaning the result will be evicted from the cache after 60 seconds.
This works both globally or on individual async executions.::

    # simple cached example
    from django_q.tasks import async, result

    # cache the result for 10 seconds
    id = async('math.floor', 100, cached=10)

    # wait max 50ms for the result to appear in the cache
    result(id, wait=50, cached=True)

    # o fetch the task object
    task = fetch(id, cache=True)

    # and then save it to the database
    task.save()

This also works for group actions::

    # cached group example
    from django_q.tasks import async, result_group
    from django_q.brokers import get_broker

    # set up a broker instance for better performance
    broker = get_broker()

    # async a hundred functions under a group label
    for i in range(100):
        async('math.frexp',
              i,
              group='frexp',
              cached=True,
              broker=broker)

    # wait max 50ms for one hundred results to return
    result_group('frexp', wait=50, count=100, cached=True)

Note that exact same result can be achieved by using the more convenient :func:`async_iter` in this case, but without hook support.

Synchronous testing
-------------------

:func:`async` can be instructed to execute a task immediately by setting the optional keyword ``sync=True``.
The task will then be injected straight into a worker and the result saved by a monitor instance::

    from django_q.tasks import async, fetch

    # create a synchronous task
    task_id = async('my.buggy.code', sync=True)

    # the task will then be available immediately
    task = fetch(task_id)

    # and can be examined
    if not task.success:
        print('An error occurred: {}'.format(task.result))

.. code:: bash

    An error occurred: ImportError("No module named 'my'",)

Note that :func:`async` will block until the task is executed and saved. This feature bypasses the broker and is intended for debugging and development.
Instead of setting ``sync`` on each individual ``async`` you can also configure :ref:`sync` as a global override.

Connection pooling
------------------

Django Q tries to pass broker instances around its parts as much as possible to save you from running out of connections.
When you are making individual calls to :func:`async` a lot though, it can help to set up a broker to reuse for :func:`async`:

.. code:: python

    # broker connection economy example
    from django_q.tasks import async
    from django_q.brokers import get_broker

    broker = get_broker()
    for i in range(50):
        async('math.modf', 2.5, broker=broker)

.. tip::

    If you are using `django-redis <https://github.com/niwinz/django-redis>`__  and the redis broker, you can :ref:`configure <django_redis>` Django Q to use its connection pool.


Reference
---------

.. py:function:: async(func, *args, hook=None, group=None, timeout=None,\
    save=None, sync=False, cached=False, broker=None, q_options=None, **kwargs)

    Puts a task in the cluster queue

   :param object func: The task function to execute
   :param tuple args: The arguments for the task function
   :param object hook: Optional function to call after execution
   :param str group: An optional group identifier
   :param int timeout: Overrides global cluster :ref:`timeout`.
   :param bool save: Overrides global save setting for this task.
   :param bool sync: If set to True, async will simulate a task execution
   :param cached: Output the result to the cache backend. Bool or timeout in seconds
   :param broker: Optional broker connection from :func:`brokers.get_broker`
   :param dict q_options: Options dict, overrides option keywords
   :param dict kwargs: Keyword arguments for the task function
   :returns: The uuid of the task
   :rtype: str

.. py:function:: result(task_id, wait=0, cached=False)

    Gets the result of a previously executed task

    :param str task_id: the uuid or name of the task
    :param int wait: optional milliseconds to wait for a result
    :param bool cached: run this against the cache backend.
    :returns: The result of the executed task

.. py:function:: fetch(task_id, wait=0, cached=False)

    Returns a previously executed task

    :param str name: the uuid or name of the task
    :param int wait: optional milliseconds to wait for a result
    :param bool cached: run this against the cache backend.
    :returns: A task object
    :rtype: Task

    .. versionchanged:: 0.2.0

    Renamed from get_task

.. py:function:: async_iter(func, args_iter,**kwargs)

   Runs iterable arguments against the cache backend and returns a single collated result

   :param object func: The task function to execute
   :param args: An iterable containing arguments for the task function
   :param dict kwargs: Keyword arguments for the task function. Ignores ``cached`` and ``hook``.
   :returns: The uuid of the task
   :rtype: str

.. py:function:: queue_size()

    Returns the size of the broker queue.
    Note that this does not count tasks currently being processed.

    :returns: The amount of task packages in the broker
    :rtype: int

.. py:function:: result_group(group_id, failures=False, wait=0, count=None, cached=False)

    Returns the results of a task group

    :param str group_id: the group identifier
    :param bool failures: set this to ``True`` to include failed results
    :param int wait: optional milliseconds to wait for a result or count
    :param int count: block until there are this many results in the group
    :param bool cached: run this against the cache backend
    :returns: a list of results
    :rtype: list

.. py:function:: fetch_group(group_id, failures=True, wait=0, count=None, cached=False)

    Returns a list of tasks in a group

    :param str group_id: the group identifier
    :param bool failures: set this to ``False`` to exclude failed tasks
    :param int wait: optional milliseconds to wait for a task or count
    :param int count: block until there are this many tasks in the group
    :param bool cached: run this against the cache backend.
    :returns: a list of :class:`Task`
    :rtype: list

.. py:function:: count_group(group_id, failures=False, cached=False)

    Counts the number of task results in a group.

    :param str group_id: the group identifier
    :param bool failures: counts the number of failures if ``True``
    :param bool cached: run this against the cache backend.
    :returns: the number of tasks or failures in a group
    :rtype: int

.. py:function:: delete_group(group_id, tasks=False, cached=False)

    Deletes a group label from the database.

    :param str group_id: the group identifier
    :param bool tasks: also deletes the associated tasks if ``True``
    :param bool cached: run this against the cache backend.
    :returns: the numbers of tasks affected
    :rtype: int

.. py:function:: delete_cached(task_id, broker=None)

    Deletes a task from the cache backend

    :param task_id: the uuid of the task
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