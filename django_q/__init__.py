"""
A multiprocessing task queue application for Django
Author: Ilan Steemers (koed00@gmail.com
Github: https://github.com/Koed00/django-q
"""

from django_q.q import Cluster, async

default_app_config = 'django_q.apps.SessionAdminConfig'
