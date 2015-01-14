import logging
from functools import partial
from multiprocessing import Process

log = logging.getLogger(__name__)


def spawnable(func=None, debug=False):
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

    def inner(inner_func):
        def spawn(*args, **kwargs):
            log.debug('Spawn process [%s]', inner_func.__name__)
            args = args

            if debug:
                log.warning('debug is set, running inline')
                return inner_func(*args, **kwargs)

            p = Process(target=inner_func, args=args, kwargs=kwargs)
            p.start()

        setattr(inner_func, 'spawn', spawn)

        return inner_func

    if func is None:
        return inner

    return inner(func)
