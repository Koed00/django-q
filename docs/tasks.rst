Tasks
=====

Use  :py:func:`async` from your code to quickly offload tasks to the py:module:`cluster`:

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

.. py:function:: async(func, *args, [hook=None,] **kwargs)

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

.. py:function:: get_task(name)

    Returns a previously executed task

    :param str name: the name of the task
    :returns: The task
    :rtype: Task


.. py:class:: Task

    Database model describing an executed task