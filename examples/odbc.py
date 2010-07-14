#-*- coding: utf-8 -*-

"""Example pyDBCLI.utils.Utility app, using PyODBC to wrap
DBAPI cursor calls, allowing the use an ODBC DSN and driver
for connections and to send queries.
"""
__author__ = 'Wes Mason <wes[at]1stvamp[dot]org>'
__docformat__ = 'restructuredtext en'
__version__ = '0.1'

import pyodbc
import getopt
import sys
from urlparse import urlparse
from pyDBCLI.utils import Utility
from pyDBCLI.helpers import error, usage, memoized

class ODBCUtility(Utility):
        prompt = 'odbc-qt# '
        intro = 'ODBC Query Tool v%s' % (__version__,)
        query = ''
        dsn = {}

        @memoized()
        def get_tables(self):
                tables = [['Table name']]
                for row in self.cursor.tables():
                        tables.append([row])
                return tables

        @memoized()
        def get_columns(self, name):
                columns = [['Column name', 'Type', 'Size',]]
                r = self.connect.execute('SELECT * FROM %s LIMIT 1' % (table,))
                for row in r.cursor.description:
                        columns.append([row[0], self.db_types[row[1]], row[3],])
                return columns

        def connect(self, schema):
                self.dsn['schema'] = schema
                try:
                        conn = pyodbc.connect(self.query, **self.dsn)
                        self.cursor = self.system_cursor = conn.cursor()
                except:
                        error(e, False)
                        return False
                else:
                        return True

# Shell script usage instrunctions, pushed to stdout
# by usage()
USAGE_MESSAGE = """ODBC Query Tool
Usage: odbc.py -d <dsn url>

Options:
    -d, --dsn : ODBC DSN, in RFC1738 URL format:
        driver://username:password@host:port/schema
        driver://username:password@host:port/schema?extraProperties=here&another=too
"""

def url_to_dsn(url):
        res = urlparse(url)
        return res.query.replace('&', ';'), {
                'driver': res.scheme,
                'server': res.netloc,
                'database': res.path,
                'uid': res.username,
                'pwd': res.password,
        }


def main(argv):
        """Main entry function for CLI script, should be
        passed CLI args tuple, normally from sys.argv
        """
        # Get CLI options
        try:
                opts, args = getopt.getopt(
                        argv,
                        "d:",
                        [
                                "dsn=",
                        ]
                )
        except getopt.GetoptError:
                error("Unknown options", True, USAGE_MESSAGE)

        if not opts:
                usage(USAGE_MESSAGE)
                sys.exit(0)

        dsn = None
        query = None

        # Parse CLI options
        for opt, arg in opts:
                if opt in ("-d", "--dsn"):
                        query, dsn = url_to_dsn(arg)
        if not dsn:
                error("Please provide a DSN URL", True, USAGE_MESSAGE)

        # Setup cursor
        conn = pyodbc.connect(query, **dsn)

        u = ODBCUtility()
        u.cursor = u.system_cursor = conn.cursor()
        u.cmdloop()

if __name__ == "__main__":
        # Pass all CLI args except the first one, which is normally
        # the scripts filename
        main(sys.argv[1:])

