#!/usr/bin/env python
"""
check_nagios_checkresult

Icinga plugin to retrieve status from Nagios CGIs

Copyright (C) 2020 NETWAYS GmbH <info@netways.de>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import sys
import argparse
import json
import urllib2
import ssl

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3
STATUS = [
    'OK',
    'WARNING',
    'CRITICAL',
    'UNKNOWN'
]


def nagios_output(rc, output, long_output=None, perfdata=None, prefix_state=False):
    if prefix_state:
        print("[%s] %s" % (STATUS[rc], output))
    else:
        print(output)

    if long_output:
        print(long_output.strip())

    if perfdata:
        if isinstance(perfdata, list):
            text = ''
            for data in perfdata:
                text += ' %s' % data
        else:
            text = ' ' + perfdata
        print("|%s" % text)

    return rc


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(description="Icinga plugin to retrieve status from Nagios CGIs")

    parser.add_argument('--cgi', required=True,
                        help='Location of Nagios CGI root (e.g. https://nagios.example.com/nagios/cgi-bin')

    parser.add_argument('--username', '-u', help='Username for basic authentication')
    parser.add_argument('--password', '-p', help='Password for basic authentication')

    parser.add_argument('--host', '-H', help='Host name in Nagios', required=True)
    parser.add_argument('--service', '-S', help='Service name in Nagios')

    parser.add_argument('--timeout', '-t', help='Timeout for the request', type=int)
    parser.add_argument('--insecure', help='Ignore TLS/SSL trust', action='store_true')

    return parser.parse_args(argv)


def main():
    try:
        args = parse_arguments()
    except Exception as e:
        return nagios_output(UNKNOWN, "Error parsing arguments: %s" % e)

    ssl_ctx = ssl.create_default_context()
    if args.insecure:
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

    https_handler = urllib2.HTTPSHandler(context=ssl_ctx)

    if args.username and args.password:
        auth_handler = urllib2.HTTPBasicAuthHandler(urllib2.HTTPPasswordMgrWithDefaultRealm())
        auth_handler.add_password(realm=None,
                                  uri=args.cgi,
                                  user=args.username,
                                  passwd=args.password)
        opener = urllib2.build_opener(https_handler, auth_handler)
    else:
        opener = urllib2.build_opener(https_handler)

    nagios_type = 'host'
    uri = '%s/statusjson.cgi?query=%s&hostname=%s' % (
        args.cgi,
        nagios_type,
        urllib2.quote(args.host)
    )

    if args.service:
        nagios_type = 'service'
        uri += '&servicedescription=%s' % urllib2.quote(args.service)

    request = urllib2.Request(uri, headers={'Accept': 'application/json'})
    try:
        response = opener.open(request, timeout=args.timeout)
    except urllib2.URLError as e:
        return nagios_output(UNKNOWN, 'Error during HTTP request: %s - %s' % (uri, e))

    try:
        data = json.load(response)
    except Exception:
        return nagios_output(UNKNOWN, 'Could not parse JSON response: %s' % uri)

    if 'data' not in data or nagios_type not in data['data']:
        return nagios_output(UNKNOWN, 'Missing status data for %s: %s%s' % (
            nagios_type,
            args.host,
            (' ' + args.service) if args.service else ''
        ))

    status = data['data'][nagios_type]
    return nagios_output(
        status['last_hard_state'],
        status['plugin_output'],
        status['long_plugin_output'],
        status['perf_data'],
    )


if __name__ == '__main__':
    try:
        rc = main()
    except Exception as e:
        rc = nagios_output(UNKNOWN, "Generic Python error: %s" % e)

    sys.exit(rc)
