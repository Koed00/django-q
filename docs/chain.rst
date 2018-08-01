.. py:currentmodule:: django_q

Chains
======
Sometimes you want to run tasks sequentially. For that you can use the :func:`async_chain` function:

.. code-block:: python

    # async a chain of tasks
    from django_q.tasks import async_chain, result_group

    # the chain must be in the format
    # [(func,(args),{kwargs}),(func,(args),{kwargs}),..]
    group_id = async_chain([('math.copysign', (1, -1)),
                              ('math.floor', (1,))])

    # get group result
    result_group(group_id, count=2)

A slightly more convenient way is to use a :class:`Chain` instance:

.. code-block:: python

    # Chain async
    from django_q.tasks import Chain

    # create a chain that uses the cache backend
    chain = Chain(cached=True)

    # add some tasks
    chain.append('math.copysign', 1, -1)
    chain.append('math.floor', 1)

    # run it
    chain.run()

    print(chain.result())
.. code-block:: python

    [-1.0, 1]

Reference
---------
.. py:function:: async_chain(chain, group=None, cached=Conf.CACHED, sync=Conf.SYNC, broker=None)

    Async a chain of tasks. See also the :class:`Chain` class.

    :param list chain: a list of tasks in the format [(func,(args),{kwargs}), (func,(args),{kwargs})]
    :param str group: an optional group name.
    :param bool cached: run this against the cache backend
    :param bool sync: execute this inline instead of asynchronous

.. py:class:: Chain(chain=None, group=None, cached=Conf.CACHED, sync=Conf.SYNC)

    A sequential chain of tasks. Acts as a convenient wrapper for :func:`async_chain`
    You can pass the task chain at construction or you can append individual tasks before running them.

        :param list chain: a list of task in the format [(func,(args),{kwargs}), (func,(args),{kwargs})]
        :param str group: an optional group name.
        :param bool cached: run this against the cache backend
        :param bool sync: execute this inline instead of asynchronous


    .. py:method:: append(func, *args, **kwargs)

    Append a task to the chain. Takes the same arguments as :func:`async_task`

        :return: the current number of tasks in the chain
        :rtype: int


    .. py:method:: run()

    Start queueing the chain to the worker cluster.

        :return: the chains group id


    .. py:method:: result(wait=0)

    return the full list of results from the chain when it finishes. Blocks until timeout or result.

        :param int wait: how many milliseconds to wait for a result
        :return: an unsorted list of results


    .. py:method:: fetch(failures=True, wait=0)

    get the task result objects from the chain when it finishes. Blocks until timeout or result.

        :param failures: include failed tasks
        :param int wait: how many milliseconds to wait for a result
        :return: an unsorted list of task objects

    .. py:method:: current()

    get the index of the currently executing chain element

        :return int: current chain index

    .. py:method:: length()

    get the length of the chain

        :return int: length of the chain
