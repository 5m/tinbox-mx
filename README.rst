================================================================================
 tinbox-mx
================================================================================

Create tinbox tickets by importing mail from IMAP

Usage:

.. code-block:: bash
    
    mx import [options] [-v...]
    mx -? | --help
    mx --version

Options::

    -h --host <host>            IMAP host [default: imap.gmail.com]
    -u --username <username>    IMAP account username, can also be set through env IMAP_USERNAME
    -p --password <password>    IMAP account password, can also be set through env IMAP_PASSWORD
    --interval N                Check for new mail by polling every N seconds [default: 30]
    --subscribe                 Subscribe for new mail event instead of polling
    --pid FILE                  Create pid file FILE [default: /tmp/mx.pid]
    --logto FILE                Log output to FILE instead of console
    -v                          Enable verbose output
    --version                   Show version
    -? --help                   Show this screen
