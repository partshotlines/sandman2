#!/usr/bin/env python
"""sandman2ctl is a wrapper around the sandman2 library, which creates REST API
services automatically from existing databases."""

import sys
import argparse
from sandman2 import get_app

def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(
        description='Auto-generate a RESTful API service '
        'from an existing database.'
        )
    parser.add_argument(
        'URI',
        help='Database URI in the format '
             'postgresql+psycopg2://user:password@host/database')
    parser.add_argument(
        '-d',
        '--debug',
        help='Turn on debug logging',
        action='store_true',
        default=False)
    parser.add_argument(
        '-p',
        '--port',
        help='Port for service to listen on',
        default=5000)
    parser.add_argument(
        '-l',
        '--local-only',
        help='Only provide service on localhost (will not be accessible'
             ' from other machines)',
        action='store_true',
        default=False)
    parser.add_argument(
        '-r',
        '--read-only',
        help='Make all database resources read-only (i.e. only the HTTP GET method is supported)',
        action='store_true',
        default=False)
    parser.add_argument(
        '-s',
        '--schema',
        help='Use this named schema instead of default',
        default=None)
    # addition - aadel - 2017-07-26 - adding the ability to exluded tables as a space separated list eg: -e 'table1 table2 table3'
    parser.add_argument(
        '-e',
        '--exclude-tables',
        help='Exclude these tables from the api',
        default=None)
    # addition - aadel - 2017-07-26 - added the ability to run the webserver asyncronously with tornado
    parser.add_argument(
        '-t',
        '--tornado',
        help='Run with tornado web server',
        action='store_true',
        default=False)
    parser.add_argument('-m',
        '--models',
        help='Include these space separated user defined models from PYTHONPATH',
        default=None)
    # addition - aadel - 2017-07-28 - adding zlib compression
    parser.add_argument('-c',
        '--compress',
        help='Compress stream before sending data',
        action='store_true',
        default=False)

    args = parser.parse_args()
    user_models = []
    if args.models:
        user_models = args.models.split()
    # addition - aadel - 2017-07-26 - exclude tables if set
    exclude_tables = []
    if args.exclude_tables:
        exclude_tables = args.exclude_tables.split()

    app = get_app(args.URI, read_only=args.read_only, schema=args.schema, exclude_tables=exclude_tables, user_models=user_models, compress=args.compress)
    if args.debug:
        app.config['DEBUG'] = True
    if args.local_only:
        host = '127.0.0.1'
    else:
        host = '0.0.0.0'
    app.config['SECRET_KEY'] = '42'

    # run with tornado, this should be the default production option
    if args.tornado:
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop

        app = WSGIContainer(app)
        app.debug = args.debug
        http_server = HTTPServer(app)
        http_server.start(0)
        http_server.listen(args.port, address=host)
        IOLoop.instance().start()
    else:
        app.run(host=host, port=int(args.port))


if __name__ == '__main__':
    main()
