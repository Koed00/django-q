# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_q',
 'django_q.brokers',
 'django_q.management',
 'django_q.management.commands',
 'django_q.migrations',
 'django_q.tests',
 'django_q.tests.testing_utilities']

package_data = \
{'': ['*'], 'django_q': ['locale/de/LC_MESSAGES/*', 'locale/fr/LC_MESSAGES/*']}

install_requires = \
['arrow>=1.1.0,<2.0.0',
 'blessed>=1.17.6,<2.0.0',
 'django-picklefield>=3.0.1,<4.0.0',
 'django>=2.2,<4.0.0']

extras_require = \
{'rollbar': ['django-q-rollbar>=0.1'],
 'sentry': ['django-q-sentry>=0.1'],
 'testing': ['hiredis>=1.0.1,<2.0.0',
             'psutil>=5.7.0,<6.0.0',
             'django-redis>=4.12.1,<5.0.0',
             'iron-mq>=0.9,<0.10',
             'boto3>=1.14.12,<2.0.0',
             'pymongo>=3.10.1,<4.0.0',
             'croniter>=0.3.34,<0.4.0']}

entry_points = \
{'djangoq.errorreporters': ['rollbar = django_q_rollbar:Rollbar',
                            'sentry = django_q_sentry:Sentry']}

setup_kwargs = {
    'name': 'django-q',
    'version': '2.0.1',
    'description': 'A multiprocessing distributed task queue for Django',
    'long_description': ".. image:: docs/_static/logo.png\n    :align: center\n    :alt: Q logo\n    :target: https://django-q.readthedocs.org/\n\nA multiprocessing distributed task queue for Django\n---------------------------------------------------\n\n|image0| |image1| |docs| |image2|\n\nFeatures\n~~~~~~~~\n\n-  Multiprocessing worker pool\n-  Asynchronous tasks\n-  Scheduled, cron and repeated tasks\n-  Signed and compressed packages\n-  Failure and success database or cache\n-  Result hooks, groups and chains\n-  Django Admin integration\n-  PaaS compatible with multiple instances\n-  Multi cluster monitor\n-  Redis, Disque, IronMQ, SQS, MongoDB or ORM\n-  Rollbar and Sentry support\n\nRequirements\n~~~~~~~~~~~~\n\n-  `Django <https://www.djangoproject.com>`__ > = 2.2\n-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__\n-  `Arrow <https://github.com/crsmithdev/arrow>`__\n-  `Blessed <https://github.com/jquast/blessed>`__\n\nTested with: Python 3.7, 3.8, 3.9 Django 2.2.X and 3.2.X\n\n.. warning:: Since Python 3.7 `async` became a reserved keyword and was refactored to `async_task`\n\nBrokers\n~~~~~~~\n- `Redis <https://django-q.readthedocs.org/en/latest/brokers.html#redis>`__\n- `Disque <https://django-q.readthedocs.org/en/latest/brokers.html#disque>`__\n- `IronMQ <https://django-q.readthedocs.org/en/latest/brokers.html#ironmq>`__\n- `Amazon SQS <https://django-q.readthedocs.org/en/latest/brokers.html#amazon-sqs>`__\n- `MongoDB <https://django-q.readthedocs.org/en/latest/brokers.html#mongodb>`__\n- `Django ORM <https://django-q.readthedocs.org/en/latest/brokers.html#django-orm>`__\n\nInstallation\n~~~~~~~~~~~~\n\n-  Install the latest version with pip::\n\n    $ pip install django-q\n\n\n-  Add `django_q` to your `INSTALLED_APPS` in your projects `settings.py`::\n\n       INSTALLED_APPS = (\n           # other apps\n           'django_q',\n       )\n\n-  Run Django migrations to create the database tables::\n\n    $ python manage.py migrate\n\n-  Choose a message `broker <https://django-q.readthedocs.org/en/latest/brokers.html>`__ , configure and install the appropriate client library.\n\nRead the full documentation at `https://django-q.readthedocs.org <https://django-q.readthedocs.org>`__\n\n\nConfiguration\n~~~~~~~~~~~~~\n\nAll configuration settings are optional. e.g:\n\n.. code:: python\n\n    # settings.py example\n    Q_CLUSTER = {\n        'name': 'myproject',\n        'workers': 8,\n        'recycle': 500,\n        'timeout': 60,\n        'compress': True,\n        'cpu_affinity': 1,\n        'save_limit': 250,\n        'queue_limit': 500,\n        'label': 'Django Q',\n        'redis': {\n            'host': '127.0.0.1',\n            'port': 6379,\n            'db': 0, }\n    }\n\nFor full configuration options, see the `configuration documentation <https://django-q.readthedocs.org/en/latest/configure.html>`__.\n\nManagement Commands\n~~~~~~~~~~~~~~~~~~~\n\nStart a cluster with::\n\n    $ python manage.py qcluster\n\nMonitor your clusters with::\n\n    $ python manage.py qmonitor\n\nMonitor your clusters' memory usage with::\n\n    $ python manage.py qmemory\n\nCheck overall statistics with::\n\n    $ python manage.py qinfo\n\nCreating Tasks\n~~~~~~~~~~~~~~\n\nUse `async_task` from your code to quickly offload tasks:\n\n.. code:: python\n\n    from django_q.tasks import async_task, result\n\n    # create the task\n    async_task('math.copysign', 2, -2)\n\n    # or with a reference\n    import math.copysign\n\n    task_id = async_task(copysign, 2, -2)\n\n    # get the result\n    task_result = result(task_id)\n\n    # result returns None if the task has not been executed yet\n    # you can wait for it\n    task_result = result(task_id, 200)\n\n    # but in most cases you will want to use a hook:\n\n    async_task('math.modf', 2.5, hook='hooks.print_result')\n\n    # hooks.py\n    def print_result(task):\n        print(task.result)\n\nFor more info see `Tasks <https://django-q.readthedocs.org/en/latest/tasks.html>`__\n\n\nSchedule\n~~~~~~~~\n\nSchedules are regular Django models. You can manage them through the\nAdmin page or directly from your code:\n\n.. code:: python\n\n    # Use the schedule function\n    from django_q.tasks import schedule\n\n    schedule('math.copysign',\n             2, -2,\n             hook='hooks.print_result',\n             schedule_type=Schedule.DAILY)\n\n    # Or create the object directly\n    from django_q.models import Schedule\n\n    Schedule.objects.create(func='math.copysign',\n                            hook='hooks.print_result',\n                            args='2,-2',\n                            schedule_type=Schedule.DAILY\n                            )\n\n    # Run a task every 5 minutes, starting at 6 today\n    # for 2 hours\n    import arrow\n\n    schedule('math.hypot',\n             3, 4,\n             schedule_type=Schedule.MINUTES,\n             minutes=5,\n             repeats=24,\n             next_run=arrow.utcnow().replace(hour=18, minute=0))\n\n    # Use a cron expression\n    schedule('math.hypot',\n             3, 4,\n             schedule_type=Schedule.CRON,\n             cron = '0 22 * * 1-5')\n\nFor more info check the `Schedules <https://django-q.readthedocs.org/en/latest/schedules.html>`__ documentation.\n\n\nTesting\n~~~~~~~\n\nTo run the tests you will need the following in addition to install requirements:\n\n* `py.test <http://pytest.org/latest/>`__\n* `pytest-django <https://github.com/pytest-dev/pytest-django>`__\n* Disque from https://github.com/antirez/disque.git\n* Redis\n* MongoDB\n\nOr you can use the included Docker Compose file.\n\nThe following commands can be used to run the tests:\n\n.. code:: bash\n\n    # Create virtual environment\n    python -m venv venv\n\n    # Install requirements\n    venv/bin/pip install -r requirements.txt\n\n    # Install test dependencies\n    venv/bin/pip install pytest pytest-django\n\n    # Install django-q\n    venv/bin/python setup.py develop\n\n    # Run required services (you need to have docker-compose installed)\n    docker-compose -f test-services-docker-compose.yaml up -d\n\n    # Run tests\n    venv/bin/pytest\n\n    # Stop the services required by tests (when you no longer plan to run tests)\n    docker-compose -f test-services-docker-compose.yaml down\n\nLocale\n~~~~~~\n\nCurrently available in English, German and French.\nTranslation pull requests are always welcome.\n\nTodo\n~~~~\n\n-  Better tests and coverage\n-  Less dependencies?\n\nAcknowledgements\n~~~~~~~~~~~~~~~~\n\n-  Django Q was inspired by working with\n   `Django-RQ <https://github.com/ui/django-rq>`__ and\n   `RQ <https://github.com/ui/django-rq>`__\n-  Human readable hashes by\n   `HumanHash <https://github.com/zacharyvoase/humanhash>`__\n-  Redditors feedback at `r/django <https://www.reddit.com/r/django/>`__\n\n-  JetBrains for their `Open Source Support Program <https://www.jetbrains.com/community/opensource>`__\n\n.. |image0| image:: https://github.com/koed00/django-q/workflows/Tests/badge.svg?branche=master\n   :target: https://github.com/Koed00/django-q/actions?query=workflow%3Atests\n.. |image1| image:: http://codecov.io/github/Koed00/django-q/coverage.svg?branch=master\n   :target: http://codecov.io/github/Koed00/django-q?branch=master\n.. |image2| image:: http://badges.gitter.im/Join%20Chat.svg\n   :target: https://gitter.im/Koed00/django-q\n.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest\n    :alt: Documentation Status\n    :scale: 100\n    :target: https://django-q.readthedocs.org/\n",
    'author': 'Ilan Steemers',
    'author_email': 'koed00@gmail.com',
    'maintainer': 'Ilan Steemers',
    'maintainer_email': 'koed00@gmail.com',
    'url': 'https://django-q.readthedocs.org',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)

