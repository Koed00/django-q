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

.. py:function:: async(func, *args, hook=None, **kwargs)

    Puts a task in the cluster queue

   :param func: The task function to execute
   :param args: The arguments for the task function
   :type func: str or object
   :param hook: Optional function to call after execution
   :type hook: str or object
   :param kwargs: Keyword arguments for the task function
   :returns: The name of the task
   :rtype: str

.. py:function:: result(name)

    Gets the result of a previously executed task

    :param str name: the name of the task
    :returns: The result of the executed task

.. py:function:: fetch(name)

    Returns a previously executed task

    :param str name: the name of the task
    :returns: The task
    :rtype: Task

    .. versionchanged:: 0.2.0

    Renamed from get_task

.. py:class:: Task

    Database model describing an executed task

    .. py:attribute:: name

    The name of the task

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

    The moment the task was picked up by a worker

    .. py:attribute:: stopped

    The moment a worker finished this task

    .. py:attribute:: success

    Was the task executed without problems?

    .. py:method:: time_taken

    Calculates the difference in seconds between started and stopped

    .. py:classmethod:: get_result(task_name)

     Get a result directly by task name

.. py:class:: Success

    A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is True.

.. py:class:: Failure

     A proxy model of :class:`Task` with the queryset filtered on :attr:`Task.success` is False.