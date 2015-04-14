"""
Create tickets by importing mail from IMAP

Usage:
  mx import [options] [-v...]
  mx -? | --help
  mx --version

Options:
  -h --host <host>            IMAP host [default: imap.gmail.com]
  -u --username <username>    IMAP account username
  -p --password <password>    IMAP account password
  --interval N                Check for new mail by polling every N seconds [default: 30]
  --subscribe                 Subscribe for new mail event instead of polling
  --pid FILE                  Create pid file FILE [default: /tmp/mx.pid]
  --logto FILE                Log output to FILE instead of console
  -v                          Enable verbose output
  --version                   Show version
  -? --help                   Show this screen

"""
import json
import logging
import logging.config
import os
import signal
from docopt import docopt
from getpass import getpass
from time import sleep

from . import log
from .processing import spawnable
from .. import __version__, imap, message
from ..stores.trak import insert
from ..stores.errors import BackendError

logger = logging.getLogger(__name__)


class Interface(object):

    _quit = False
    _retry = False

    def __init__(self):
        # Parse command options
        self.opts = docopt(__doc__, version='mx v{}'.format(__version__))

        # Setup logging
        self.setup_logging()
        logger.info('Start mx...')

        # Listen to OS signals
        self.register_signals(catch_all=False)

        # Create PID file
        if self.opts['--pid']:
            self.create_pidfile()

        # Ensure credential options, prompt missing
        self.ensure_credentials()

        # Start command loop
        try:
            self.run()
        except Exception as e:
            logger.exception(e)
        finally:
            self.quit()

    def run(self):
        while not self._quit:
            try:
                if self.opts['--subscribe']:
                    # MODE: Subscribe
                    with imap.login(**self.imap_settings) as subscriber:
                        # Blocks with callback
                        subscriber.subscribe(self.import_mail.spawn)
                else:
                    # MODE: Polling
                    self.import_mail()
                    if not self._quit:
                        interval = self.opts['--interval']
                        logger.debug('Sleep for %s seconds...', interval)
                        sleep(float(interval))

            except ConnectionError as e:
                logger.critical('Connection error: %s', e)
                self._retry = True
            except ValueError as e:
                logger.error('IMAP error: %s', e)
                self._retry = True
            except InterruptedError:
                continue  # Interrupted by signal, re-loop

            if self._retry:
                wait = 30
                logger.debug('Retry in %s seconds...', wait)
                sleep(wait)

    @spawnable
    def import_mail(self):
        with imap.login(**self.imap_settings) as client:
            for index, uid, msg in client.fetch_unseen():
                try:
                    mail = message.parse(msg)
                    logger.info('New mail: %s', mail.subject)

                    # Insert mail into trak
                    insert(mail)

                    # TODO: Submit message to remote API
                    # TODO: Delete if successfully submitted?
                    #       CLI option --delete?

                except BackendError:
                    logger.error('Failed to import mail: %s', uid)
                    client.mark_unseen(index)
                    # TODO: Catch correct api exception
                    # TODO: Handle failed api call, mark as unseen. Flag with
                    #       try-count? Delete after X tries?

                except Exception:
                    logger.error('Failed to parse mail: %s', uid)
                    # TODO: Create custom parse exception
                    # TODO: Handle mail parse error. Move to other mailbox?
                    #       eave as seen?

    @property
    def imap_settings(self):
        return {
            'host': self.opts['--host'],
            'username': self.opts['--username'],
            'password': self.opts['--password'],
            'debug_level': self.opts['-v'] - 1
        }

    def setup_logging(self):
        filename = self.opts['--logto']
        verbose = self.opts['-v']
        log.configure(filename, verbose)

    def register_signals(self, catch_all=True):
        signal.signal(signal.SIGHUP, lambda *args: self.reload())  # 1; Reload
        signal.signal(signal.SIGINT, lambda *args: self.abort())   # 2; Interrupt, ctrl-c
        signal.signal(signal.SIGTERM, lambda *args: self.stop())   # 15; Stop

        if catch_all:
            exclude_signals = (
                signal.SIGHUP, signal.SIGINT, signal.SIGTERM,    # Our dispatched
                signal.SIG_DFL, signal.SIGKILL, signal.SIGSTOP   # Non-catchable
            )
            signals = (s for s in dir(signal) if s.startswith('SIG'))
            signals = {s for s in map(lambda n: getattr(signal, n), signals)}
            signals = filter(lambda s: s not in exclude_signals, signals)
            print_signal = lambda s, f: logger.warn('*** GOT SIGNAL %s ***', s)

            for signum in signals:
                signal.signal(signum, print_signal)

    def create_pidfile(self):
        pidfile = self.opts['--pid']
        pid = os.getpid()
        with open(pidfile, 'w') as f:
            f.write(str(pid))
            logger.debug('Created PID file: %s [%s]', pidfile, pid)

    def delete_pidfile(self):
        pidfile = self.opts['--pid']
        if os.path.exists(pidfile):
            os.remove(pidfile)
            logger.debug('Cleanup PID file: %s', pidfile)

    def ensure_credentials(self):
        # Prompt for username if not given
        if not self.opts['--username']:
            self.opts['--username'] = input('Username: ')

        # Prompt for password if not given
        if not self.opts['--password']:
            self.opts['--password'] = getpass()

    def reload(self):
        logger.warn('--- SIGHUP ---')

    def abort(self):
        logger.warn('--- SIGINT ---')
        self.safe_quit()

    def stop(self):
        logger.warn('--- SIGTERM ---')
        self.safe_quit()

    def safe_quit(self):
        self._quit = True

    def quit(self):
        self.delete_pidfile()
        logger.info('Bye!')
        exit()


if __name__ == '__main__':
    Interface()