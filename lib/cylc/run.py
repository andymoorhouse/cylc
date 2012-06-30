#!/usr/bin/env python

#C: THIS FILE IS PART OF THE CYLC FORECAST SUITE METASCHEDULER.
#C: Copyright (C) 2008-2012 Hilary Oliver, NIWA
#C:
#C: This program is free software: you can redistribute it and/or modify
#C: it under the terms of the GNU General Public License as published by
#C: the Free Software Foundation, either version 3 of the License, or
#C: (at your option) any later version.
#C:
#C: This program is distributed in the hope that it will be useful,
#C: but WITHOUT ANY WARRANTY; without even the implied warranty of
#C: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#C: GNU General Public License for more details.
#C:
#C: You should have received a copy of the GNU General Public License
#C: along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Provide the main function for "cylc run" and "cylc restart"."""

import os, sys
import pwd
import subprocess
from cylc.hostname import is_remote_host

global debug
debug = True

def remote_run( name ):
    owner = None
    host = None
    argv = sys.argv[1:]
    args = []
    while argv:
        arg = argv.pop(0)
        if arg.startswith("--owner="):
            owner = arg.replace("--owner=", "")
        elif arg == "-o":
            owner = argv.pop(0)
        elif arg.startswith("--host="):
            host = arg.replace("--host=", "")
        else:
            args.append(arg)

    if ( owner
         and owner != os.environ.get("USER", pwd.getpwuid(os.getuid()).pw_name)
         or is_remote_host(host) ):
        user_at_host = ''
        if owner: 
            user_at_host = owner  + '@'
        if host:
            user_at_host += host
        else:
            user_at_host += 'localhost'

        command = ["ssh", "-oBatchMode=yes", user_at_host, "/usr/bin/env", "bash"]

        try:
            popen = subprocess.Popen( command, stdin=subprocess.PIPE )
            popen.communicate( """
for FILE in /etc/profile ~/.profile; do test -f $FILE && . $FILE; done
cylc %s %s""" % (name, ' '.join(args)) )
            res = popen.wait()
            if res < 0:
                sys.exit("command terminated by signal %d" % res)
            elif res > 0:
                sys.exit("command failed %d" % res)
        except OSError as e:
            # (note this would not catch background execution failure)
            sys.exit("Job submission failed %s" % str(e))
        else:
            # done (remote suite finished)
            sys.exit(0)

def main(name, start):

    remote_run(name)

    # local invocation
    try:
        server = start()
    except Exception, x:
        if debug:
            raise
        else:
            print >> sys.stderr, x
            print >> sys.stderr, "(use --debug to see exception traceback)"
            sys.exit(1)
    try:
        server.run()
        #   For profiling:
        #import cProfile
        #cProfile.run( 'server.run()', 'fooprof' )
        #   and see Python docs "The Python Profilers"
        #   for how to display the resulting stats.
    except Exception, x:
        print >> sys.stderr, "ERROR CAUGHT, will clean up before exit"
        # this assumes no exceptions in shutdown():
        server.shutdown( 'ERROR: ' + str(x) )

        if debug:
            raise
        else:
            print >> sys.stderr, "THE ERROR WAS:"
            print >> sys.stderr, x
            print >> sys.stderr, "(use --debug to see exception traceback)"
            sys.exit(1)
    except:
        # ?catch 'sys.exit(1)' and 'raise SystemExit("foo")'?
        print >> sys.stderr, "ERROR CAUGHT; will clean up before exit"
        server.shutdown('!cylc error - please report!')
        raise
    else:
        server.shutdown('Run completed normally')


def set_main_debug(mode):
    global debug
    debug = mode