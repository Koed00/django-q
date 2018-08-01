.. py:currentmodule:: django_q

Iterable
========
If you have an iterable object with arguments for a function, you can use :func:`async_iter` to async them with a single command::

    # Async Iterable example
    from django_q.tasks import async_iter, result

    # set up a list of arguments for math.floor
    iter = [i for i in range(100)]

    # async_task iter them
    id=async_iter('math.floor',iter)

    # wait for the collated result for 1 second
    result_list = result(id, wait=1000)

This will individually queue 100 tasks to the worker cluster, which will save their results in the cache backend for speed.
Once all the 100 results are in the cache, they are collated into a list and saved as a single result in the database. The cache results are then cleared.

You can also use an :class:`Iter` instance which can sometimes be more convenient:

.. code-block:: python

    from django_q.tasks import Iter

    i = Iter('math.copysign')

    # add some arguments
    i.append(1, -1)
    i.append(2, -1)
    i.append(3, -1)

    # run it
    i.run()

    # get the results
    print(i.result())

.. code-block:: python

    [-1.0, -2.0, -3.0]

Reference
---------

.. py:function:: async_iter(func, args_iter,**kwargs)

   Runs iterable arguments against the cache backend and returns a single collated result.
   Accepts the same options as :func:`async_task` except ``hook``. See also the :class:`Iter` class.

   :param object func: The task function to execute
   :param args: An iterable containing arguments for the task function
   :param dict kwargs: Keyword arguments for the task function. Ignores ``hook``.
   :returns: The uuid of the task
   :rtype: str

.. py:class:: Iter(func=None, args=None, kwargs=None, cached=Conf.CACHED, sync=Conf.SYNC, broker=None)

    An async task with iterable arguments. Serves as a convenient wrapper for :func:`async_iter`
    You can pass the iterable arguments at construction or you can append individual argument tuples.

        :param func: the function to execute
        :param args: an iterable of arguments.
        :param kwargs: the keyword arguments
        :param bool cached: run this against the cache backend
        :param bool sync: execute this inline instead of asynchronous
        :param broker: optional broker instance


    .. py:method:: append(*args)

    Append arguments to the iter set. Returns the current set count.

        :param args: the arguments for a single execution
        :return: the current set count
        :rtype: int


    .. py:method:: run()

    Start queueing the tasks to the worker cluster.

        :return: the task result id


    .. py:method:: result(wait=0)

    return the full list of results.

        :param int wait: how many milliseconds to wait for a result
        :return: an unsorted list of results


    .. py:method:: fetch(wait=0)

    get the task result objects.

        :param int wait: how many milliseconds to wait for a result
        :return: an unsorted list of task objects


    .. py:method:: length()

    get the length of the arguments list

        :return int: length of the argument list

