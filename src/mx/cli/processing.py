import logging
from functools import partial
from multiprocessing import Process

log = logging.getLogger(__name__)


def spawnable(outer_func=None, debug=False):
    """
    Decorator to make a method a blind-firing asynchronous subprocess.
    Spawns a subprocess of original when called.

    >>> import time

    >>> @spawnable
    >>> def foobar():
    ...     time.sleep(1)
    ...     print("World!")
    >>> foobar.spawn()  # Executes the method in a new subprocess
    >>> print("Hello")
    Hello
    World!

    or, if you want to disable subprocess spawning and run the function
    in-line for debugging purposes:

    >>> @spawnable(debug=True)
    >>> def foobar():
    ...     time.sleep(1)
    ...     print("World!")
    >>> foobar.spawn()  # Executes the method in-line
    >>> print("Hello")
    World!
    Hello
    """

    class Inner:
        def __init__(self, func):
            self.func = func

        def spawn(self, *args, **kwargs):
            log.debug('Spawn process [%s]', self.func.__name__)
            args = args

            if debug:
                log.warning('debug is set, running inline')
                return self.func(*args, **kwargs)

            p = Process(target=self.func,
                        args=(self.instance,) + args,
                        kwargs=kwargs)
            p.start()

        def __get__(self, instance, klass):
            self.instance = instance

            func = partial(self.func, instance)
            setattr(func, 'spawn', self.spawn)

            return func

    if outer_func is None:
        return Inner

    return Inner(outer_func)
