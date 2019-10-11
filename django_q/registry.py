from django_q.conf import logger

registry = {}


def register_schedule(**kwargs):
    def inner(func):
        func_name = func.__globals__["__name__"] + "." + func.__qualname__
        kwargs['func'] = func_name
        kwargs['from_registry'] = True
        if "name" not in kwargs:
            kwargs["name"] = func_name
        registry[kwargs["name"]] = kwargs
        logger.debug("Registered {} ({})".format(kwargs["name"], func_name))
        return func
    return inner
