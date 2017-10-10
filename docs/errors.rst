Errors
------
.. py:currentmodule:: django_q

Django Q uses a pluggable error reporter system based upon python `extras <https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies>`__, allowing anyone to develop plugins for their favorite error reporting and monitoring integration. Currently implemented examples include `Rollbar <https://rollbar.com/>`__ and `Sentry <https://docs.sentry.io/>`__.

Error reporting plugins register a class which implements a ``report`` method, which is invoked when a Django Q cluster encounters an error, passing information to the particular service. Error reporters must be :ref:`configured<error_reporter>` via the ``Q_CLUSTER`` dictionary in your :file:`settings.py`. These settings are passed as kwargs upon initiation of the Error Reporter. Therefore, in order to implement a new plugin, a package must expose a class which will be instantiated with the necessary information via the ``Q_CLUSTER`` settings and implements a single ``report`` method.

For example implementations, see `django-q-rollbar <https://github.com/danielwelch/django-q-rollbar>`__ and `django-q-sentry <https://github.com/danielwelch/django-q-sentry>`__
