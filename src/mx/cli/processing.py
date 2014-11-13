import logging
from functools import partial
from multiprocessing import Process

log = logging.getLogger(__name__)


class spawnable(object):
    """
    Attach .spawn() helper to decorated function.
    Spawns a sub process of original when called.

    @spawnable
    def foobar():
        pass

    foobar.spawn()
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, klass):
        self.instance = instance
        func = partial(self.func, instance)
        setattr(func, 'spawn', self.__spawn__)
        return func

    def __spawn__(self, *args, **kwargs):
        log.debug('Spawn process [%s]', self.func.__name__)
        args = (self.instance,) + args
        p = Process(target=self.func, args=args, kwargs=kwargs)
        p.start()
