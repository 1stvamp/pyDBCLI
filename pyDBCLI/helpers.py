#-*- coding: utf-8 -*-

"""Helper utils for pyDBCLI
"""
__author__ = 'Wes Mason <wes[at]1stvamp[dot]org>'
__docformat__ = 'restructuredtext en'
__version__ = '0.1'

import string
import sys
from functools import wraps

def usage(msg):
        """Usage message to display when running from command line.
        """
        print >> sys.stdout, msg

def error(msg, fatal=False, usage_msg=None):
        """Helper util to display an error to STDERR, then display the usage
        help info for the script and exit with an error code.
        """
        print >> sys.stderr, "\nERROR: %s" % (msg,)
        if fatal:
                if usage_msg:
                    usage(usage_msg)
                sys.exit(1)

def print_table(rows, as_keys=False, header=True, vdelim="|", padding=1, justify='center'):
        """ Outputs a list of lists as a Restructured Text Table

        - rows - list of lists
        - header - if True the first row is treated as a table header
        - vdelim - vertical delimiter betwee columns
        - padding - padding nr. of spaces are left around the longest element in the
          column
        - justify - may be left,center,right
        """

        border = "-" # character for drawing the border
        justify = {'left':string.ljust,'center':string.center, 'right':string.rjust}[justify.lower()]

        # calculate column widhts (longest item in each col
        # plus "padding" nr of spaces on both sides)
        cols = zip(*rows)
        col_widths = [max([len(str(item))+2*padding for item in col]) for col in cols]

        # the horizontal border needed by rst
        if as_keys:
                borderline = '--'
        else:
                borderline = vdelim + vdelim.join([w*border for w in col_widths]) + vdelim

        # outputs table in rst format
        print >> sys.stdout, borderline
        # Just print out in dict() style, e.g. key: value
        if as_keys:
                keys = rows[0]
                del rows[0]
                for row in rows:
                        for i, value in enumerate(row):
                                print >> sys.stdout, str(keys[i]) + ': ' + str(value)
                        print >> sys.stdout, borderline
        else:
                for row in rows:
                        print >> sys.stdout, vdelim + vdelim.join([justify(str(item),width) for (item,width) in zip(row,col_widths)]) + vdelim
                        print >> sys.stdout, borderline

class memoized(object):
        """Decorator that caches a function's return value each time it is called.
        If called later with the same arguments, the cached value is returned, and
        not re-evaluated.
        Adapted from the Memoize example at:
        http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
        """
        def __call__(self, fn):
                @wraps(fn)
                def wrapper(*args, **kwargs):
                        cache = args[0].data_cache
                        key = str(fn)+str(args)+str(kwargs)
                        try:
                                return cache[key]
                        except KeyError:
                                cache[key] = value = fn(*args)
                                return value
                        except TypeError:
                                # uncachable -- for instance, passing a list as an argument.
                                # Better to not cache than to blow up entirely.
                                return fn(*args)
                return wrapper
