#!/usr/bin/env python

"""
This script parse for a user (first arg) a mbox file (second arg)
and import mails

- create user if needed
- resolve all contacts

"""
import sys
import argparse

from pyramid.paster import get_appsettings, setup_logging
from pyramid.config import Configurator
from pyramid.settings import aslist

from caliopen.config import Configuration
from caliopen.core.config import includeme as include_caliop_core

from caliopen.web.bin.import_email import import_email
from caliopen.web.bin.setup_storage import setup_storage
from caliopen.web.bin.create_user import create_user


def shell(**kwargs):
    try:
        from IPython import embed
        from IPython.config.loader import Config
        cfg = Config()
        cfg.InteractiveShellEmbed.confirm_exit = False
        embed(config=cfg, banner1="Caliop Shell")
    except ImportError:
        # try ~IPython-0.10 API
        try:
            from IPython.Shell import IPShellEmbed as embed
            ipshell = embed(banner="Caliop Shell")
            ipshell()
        except ImportError:
            import code
            code.interact("Caliop Shell", local=locals())


def main(args=sys.argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='conffile', default='development.ini')
    subparsers = parser.add_subparsers(title="action")

    sp_import = subparsers.add_parser('import', help='import existing mailbox')
    sp_import.set_defaults(func=import_email)
    sp_import.add_argument('-f', dest='format', choices=['mbox', 'maildir'],
                           default='mbox')
    sp_import.add_argument('-p', dest='import_path')
    sp_import.add_argument('-e', dest='email')

    sp_setup_storage = subparsers.add_parser('setup',
        help='initialize the storage engine')
    sp_setup_storage.set_defaults(func=setup_storage)

    sp_create_user = subparsers.add_parser('create_user',
        help='Create a new user')
    sp_create_user.set_defaults(func=create_user)
    sp_create_user.add_argument('-e', dest='email', help='user email')
    sp_create_user.add_argument('-p', dest='password', help='password')
    sp_create_user.add_argument('-g', dest='given_name',
                                help='user given name')
    sp_create_user.add_argument('-f', dest='family_name',
                                help='user family name')

    sp_shell = subparsers.add_parser('shell')
    sp_shell.set_defaults(func=shell)

    kwargs = parser.parse_args(args[1:])
    kwargs = vars(kwargs)

    config_uri = kwargs.pop('conffile')
    func = kwargs.pop('func')

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, u'main')
    # do not declare routes and others useless includes
    del settings['pyramid.includes']

    kwargs['settings'] = settings

    config = Configurator(settings=settings)

    if func != setup_storage:  # Don't try to configure if it's not setup up
        include_caliop_core(config)
    else:
        for file in aslist(settings['caliopen.config']):
            name, path = file.split(':', 1)
            Configuration.load(path, name)
    config.end()
    func(**kwargs)


if __name__ == '__main__':
    main()
