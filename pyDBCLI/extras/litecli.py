#-*- coding: utf-8 -*-

"""Example pyDBCLI.utils.Utility app, simple replacement for sqlite3's
CLI utility.
"""
__author__ = 'Wes Mason <wes[at]1stvamp[dot]org>'
__docformat__ = 'restructuredtext en'
__version__ = '0.1'

import sqlite3
import getopt
import sys
from pyDBCLI.utils import Utility
from pyDBCLI.helpers import error, usage, memoized

class LiteUtility(Utility):
        prompt = 'litecli# '
        intro = 'My Custom SQLite interactive CLI'

        @memoized()
        def get_tables(self):
                r = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [['Table name',],]
                for row in r:
                        tables.append([row[0]])
                return tables

        @memoized()
        def get_columns(self, name):
                r = self.cursor.execute("""SELECT sql FROM sqlite_master WHERE
                                        type='table' AND name='%s'""" % (name,))
                columns = [['SQL',],]
                for row in r:
                        columns.append([row[0]])
                return columns

        def connect(self, filepath):
                try:
                        conn = sqlite3.connect(filepath)
                        self.system_cursor = self.cursor = conn.cursor()
                except:
                        error(e, False)
                        return False
                else:
                        return True


# Shell script usage instrunctions, pushed to stdout
# by usage()
USAGE_MESSAGE = """My SQLite CLI replacement
Usage: litecli.py -f <file>

Options:
    -f, --file : SQLite DB file path
"""

def main(argv):
        """Main entry function for CLI script, should be
        passed CLI args tuple, normally from sys.argv
        """
        # Get CLI options
        try:
                opts, args = getopt.getopt(
                        argv,
                        "f:",
                        [
                                "file=",
                        ]
                )
        except getopt.GetoptError:
                error("Unknown options", True, USAGE_MESSAGE)

        if not opts:
                usage(USAGE_MESSAGE)
                sys.exit(0)

        filepath = None

        # Parse CLI options
        for opt, arg in opts:
                if opt in ("-f", "--file"):
                        filepath = arg
        if not filepath:
                error("Please provide a DB filepath", True, USAGE_MESSAGE)

        # Setup cursor
        conn = sqlite3.connect(filepath)

        u = LiteUtility()
        u.cursor = u.system_cursor = conn.cursor()
        u.cmdloop()

if __name__ == "__main__":
        # Pass all CLI args except the first one, which is normally
        # the scripts filename
        main(sys.argv[1:])

