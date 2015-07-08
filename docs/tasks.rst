Tasks
=====

Use  :py:func:`async` from your code to quickly offload tasks to the :mod:`cluster`:

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

.. py:function:: async(func, *args, hook=None, redis=None, **kwargs)

    Puts a task in the cluster queue

   :param func: The task function to execute
   :param args: The arguments for the task function
   :type func: str or object
   :param hook: Optional function to call after execution
   :type hook: str or object
   :param redis: Optional redis connection
   :param kwargs: Keyword arguments for the task function
   :returns: The uuid of the task
   :rtype: str

.. py:function:: result(task_id)

    Gets the result of a previously executed task

    :param str task_id: the uuid or name of the task
    :returns: The result of the executed task

.. py:function:: fetch(task_id)

    Returns a previously executed task

    :param str name: the uuid or name of the task
    :returns: The task
    :rtype: Task

    .. versionchanged:: 0.2.0

    Renamed from get_task

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

     Get a result directly by task uuid or name

.. py:class:: Success

    A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is True.

.. py:class:: Failure

     A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is False.