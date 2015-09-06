Brokers
=======

The broker sits between your Django instances and your Django Q cluster instances, accepting and delivering task packages.
Currently we only support `Redis <http://redis.io/>`__ and `Disque <https://github.com/antirez/disque>`__, but support for other brokers is being worked on.

Clients for `Amazon SQS <https://aws.amazon.com/sqs/>`__ and `IronMQ <http://www.iron.io/mq/>`__ are TBA.


Redis
-----
The default broker for Django Q clusters.

* Atomic
* Does not need separate cache framework for monitoring
* Does not support receipts
* Requires `Redis-py <https://github.com/andymccurdy/redis-py>`__ client library: ``pip install redis``
* Can use existing :ref:`django_redis` connections.
* Configure with :ref:`redis_configuration`-py compatible configuration

Disque
------
Unlike Redis, Disque supports message receipts which make delivery to the cluster workers guaranteed. If a task never produces a failed or successful result, it will automatically be sent to the cluster again for a retry.
You can control the amount of time Disque should wait for completion of a task by configuring the :ref:`retry` setting.

* Delivery receipts
* Atomic
* Needs Django's `Cache framework <https://docs.djangoproject.com/en/1.8/topics/cache/#setting-up-the-cache>`__ configured for monitoring
* Compatible with `Tynd <https://disque.tynd.co/>`__ Disque addon on `Heroku <https://heroku.com>`__
* Still considered Alpha software
* Requires `Redis-py <https://github.com/andymccurdy/redis-py>`__ client library: ``pip install redis``
* See the :ref:`disque_configuration` configuration section for more info.

Reference
---------
The :class:`Broker` class is used internally to communicate with the different types of brokers.
You can override this class if you want to contribute and support your own broker.

.. py:class:: Broker

   .. py:method:: enqueue(task)

      Sends a task package to the broker queue and returns a tracking id.

   .. py:method:: dequeue()

      Gets a task package from the broker.

   .. py:method:: acknowledge(id)

      Notifies the broker that the task has been processed.
      Only works with brokers that support delivery receipts.

   .. py:method:: fail(id)

      Tells the broker that the message failed to be processed by the cluster.
      Only available on brokers that support this.
      Currently only occurs when a cluster fails to unpack a task package.

   .. py:method:: delete(id)

      Instructs the broker to delete this message from the queue.

   .. py:method:: purge_queue()

      Empties the current queue of all messages.

   .. py:method:: delete_queue()

      Deletes the current queue from the broker.

   .. py:method:: queue_size()

      Returns the amount of messages in the brokers queue.

   .. py:method:: ping()

      Returns True if the broker can be reached.

   .. py:method:: info()

      Shows the name and version of the currently configured broker.
