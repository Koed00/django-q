from __future__ import absolute_import
"""
Compatibility layer.

Intentionally replaces use of python-future
"""

# https://github.com/Koed00/django-q/issues/4

try:
    range = xrange
except NameError:
    range = range

