# -*- coding: utf-8 -*-
"""
    sphinx.cmdline
    ~~~~~~~~~~~~~~

    sphinx-build command-line handling.

    :copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import os
import sys
import getopt
import traceback
from os import path

from docutils.utils import SystemMessage

from sphinx import __version__
from sphinx.errors import SphinxError
from sphinx.application import Sphinx
from sphinx.util import Tee, format_exception_cut_frames, save_traceback
from sphinx.util.console import red, nocolor, color_terminal
from sphinx.util.pycompat import terminal_safe, bytes


def usage(argv, msg=None):
    if msg:
        print(msg, file=sys.stderr)
        print(file=sys.stderr)
    print("""\
Sphinx v%s
Usage: %s [options] sourcedir outdir [filenames...]
Options: -b <builder> -- builder to use; default is html
         -a        -- write all files; default is to only write \
new and changed files
         -E        -- don't use a saved environment, always read all files
         -t <tag>  -- include "only" blocks with <tag>
         -d <path> -- path for the cached environment and doctree files
                      (default: outdir/.doctrees)
         -c <path> -- path where configuration file (conf.py) is located
                      (default: same as sourcedir)
         -C        -- use no config file at all, only -D options
         -D <setting=value> -- override a setting in configuration
         -A <name=value>    -- pass a value into the templates, for HTML builder
         -n        -- nit-picky mode, warn about all missing references
         -N        -- do not do colored output
         -q        -- no output on stdout, just warnings on stderr
         -Q        -- no output at all, not even warnings
         -w <file> -- write warnings (and errors) to given file
         -W        -- turn warnings into errors
         -P        -- run Pdb on exception
Modi:
* without -a and without filenames, write new and changed files.
* with -a, write all files.
* with filenames, write these.""" % (__version__, argv[0]), file=sys.stderr)


def main(argv):
    if not color_terminal():
        # Windows' poor cmd box doesn't understand ANSI sequences
        nocolor()

    try:
        opts, args = getopt.getopt(argv[1:], 'ab:t:d:c:CD:A:ng:NEqQWw:P')
        allopts = set(opt[0] for opt in opts)
        srcdir = confdir = path.abspath(args[0])
        if not path.isdir(srcdir):
            print('Error: Cannot find source directory.', file=sys.stderr)
            return 1
        if not path.isfile(path.join(srcdir, 'conf.py')) and \
               '-c' not in allopts and '-C' not in allopts:
            print(('Error: Source directory doesn\'t '
                                 'contain conf.py file.'), file=sys.stderr)
            return 1
        outdir = path.abspath(args[1])
        if not path.isdir(outdir):
            print('Making output directory...', file=sys.stderr)
            os.makedirs(outdir)
    except (IndexError, getopt.error):
        usage(argv)
        return 1

    filenames = args[2:]
    err = 0
    for filename in filenames:
        if not path.isfile(filename):
            print('Cannot find file %r.' % filename, file=sys.stderr)
            err = 1
    if err:
        return 1

    # likely encoding used for command-line arguments
    try:
        locale = __import__('locale')  # due to submodule of the same name
        likely_encoding = locale.getpreferredencoding()
    except Exception:
        likely_encoding = None

    buildername = None
    force_all = freshenv = warningiserror = use_pdb = False
    status = sys.stdout
    warning = sys.stderr
    error = sys.stderr
    warnfile = None
    confoverrides = {}
    tags = []
    doctreedir = path.join(outdir, '.doctrees')
    for opt, val in opts:
        if opt == '-b':
            buildername = val
        elif opt == '-a':
            if filenames:
                usage(argv, 'Cannot combine -a option and filenames.')
                return 1
            force_all = True
        elif opt == '-t':
            tags.append(val)
        elif opt == '-d':
            doctreedir = path.abspath(val)
        elif opt == '-c':
            confdir = path.abspath(val)
            if not path.isfile(path.join(confdir, 'conf.py')):
                print(('Error: Configuration directory '
                                     'doesn\'t contain conf.py file.'), file=sys.stderr)
                return 1
        elif opt == '-C':
            confdir = None
        elif opt == '-D':
            try:
                key, val = val.split('=')
            except ValueError:
                print(('Error: -D option argument must be '
                                     'in the form name=value.'), file=sys.stderr)
                return 1
            try:
                val = int(val)
            except ValueError:
                if likely_encoding and isinstance(val, bytes):
                    try:
                        val = val.decode(likely_encoding)
                    except UnicodeError:
                        pass
            confoverrides[key] = val
        elif opt == '-A':
            try:
                key, val = val.split('=')
            except ValueError:
                print(('Error: -A option argument must be '
                                     'in the form name=value.'), file=sys.stderr)
                return 1
            try:
                val = int(val)
            except ValueError:
                if likely_encoding and isinstance(val, bytes):
                    try:
                        val = val.decode(likely_encoding)
                    except UnicodeError:
                        pass
            confoverrides['html_context.%s' % key] = val
        elif opt == '-n':
            confoverrides['nitpicky'] = True
        elif opt == '-N':
            nocolor()
        elif opt == '-E':
            freshenv = True
        elif opt == '-q':
            status = None
        elif opt == '-Q':
            status = None
            warning = None
        elif opt == '-W':
            warningiserror = True
        elif opt == '-w':
            warnfile = val
        elif opt == '-P':
            use_pdb = True

    if warning and warnfile:
        warnfp = open(warnfile, 'w')
        warning = Tee(warning, warnfp)
        error = warning

    try:
        app = Sphinx(srcdir, confdir, outdir, doctreedir, buildername,
                     confoverrides, status, warning, freshenv,
                     warningiserror, tags)
        app.build(force_all, filenames)
        return app.statuscode
    except KeyboardInterrupt:
        if use_pdb:
            import pdb
            print(red('Interrupted while building, starting debugger:'), file=error)
            traceback.print_exc()
            pdb.post_mortem(sys.exc_info()[2])
        return 1
    except Exception as err:
        if use_pdb:
            import pdb
            print(red('Exception occurred while building, '
                               'starting debugger:'), file=error)
            traceback.print_exc()
            pdb.post_mortem(sys.exc_info()[2])
        else:
            print(file=error)
            if isinstance(err, SystemMessage):
                print(red('reST markup error:'), file=error)
                print(terminal_safe(err.args[0]), file=error)
            elif isinstance(err, SphinxError):
                print(red('%s:' % err.category), file=error)
                print(terminal_safe(str(err)), file=error)
            else:
                print(red('Exception occurred:'), file=error)
                print(format_exception_cut_frames().rstrip(), file=error)
                tbpath = save_traceback()
                print(red('The full traceback has been saved '
                                   'in %s, if you want to report the '
                                   'issue to the developers.' % tbpath), file=error)
                print(('Please also report this if it was a user '
                                'error, so that a better error message '
                                'can be provided next time.'), file=error)
                print((
                    'Either send bugs to the mailing list at '
                    '<http://groups.google.com/group/sphinx-dev/>,\n'
                    'or report them in the tracker at '
                    '<http://bitbucket.org/birkenfeld/sphinx/issues/>. Thanks!'), file=error)
            return 1
