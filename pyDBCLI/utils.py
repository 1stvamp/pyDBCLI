#-*- coding: utf-8 -*-

"""Framework for cmd.Cmd based interactive CLI database utils
"""
__author__ = 'Wes Mason <wes[at]1stvamp[dot]org>'
__docformat__ = 'restructuredtext en'
__version__ = '0.1'

import sys
import getopt
import re
import cmd
from datetime import datetime, date

from pyDBCLI.helpers import print_table, error


class Utility(cmd.Cmd):
        # cmd.Cmd properties
        intro = 'pyDBCLI v%s' % (__version__,)
        outro = 'Bye!'
        ruler = '-'
        prompt = 'mycli# '
        _prompt = None
        multi_prompt = '> '

        # Utility properties
        # DBAPI cursor to access profile/template
        cursor = None
        # DBAPI cursor to access system, can be the same as cursor
        system_cursor = None
        # Special d|l|c|G|x commands
        special_cmds = ['d', 'l', 'c', 'G', 'x',]
        # Current SQL command
        current = ''
        # Whether vertical print mode is on or not
        vertical_display = False
        # Cache of relation data (metadata displayed by \d)
        data_cache = {}
        # String names for DB types
        db_types = {
            str: 'text',
            bool: 'bool',
            int: 'integer',
            datetime: 'datatime',
            date: 'date',
            long: 'integer',
            float: 'real',
            unicode: 'text',
            buffer: 'blob',
            None: 'null',
        }

        def parseline(self, line):
                """Overridden Cmd.parseline so we can handle
                escaped special commands, such as \d and \G
                """
                # Hack to enforce d|l|c|G are prefixed with a \
                if re.match(self.unesc_special_cmds_re, line):
                        line = '^%s' % (line,)
                elif not self.current:
                        # Remove \ at the begining of a command
                        line = re.sub(self.special_cmds_re, r'\1\2\3', line)
                ret = cmd.Cmd.parseline(self, line)
                return ret

        def emptyline(self):
                """Overridden Cmd.emptyline so we don't re-run
                commands on a \r or \n
                """
                return False

        def print_topics(self, header, cmds, cmdlen, maxcol):
                """Overridden Cmd.print_topics so we get \ prefixed
                to the relevant commands.
                """
                if cmds:
                        self.stdout.write("%s\n"%str(header))
                        if self.ruler:
                                self.stdout.write("%s\n"%str(self.ruler * len(header)))
                        cmds = [re.sub(self.unesc_special_cmds_re, r'\\\1', cmd) for cmd in cmds]
                        self.columnize(cmds, maxcol-1)
                        self.stdout.write("\n")
                        if 'help' in cmds:
                                triggers_header = "Query triggers"
                                self.stdout.write("\n%s\n" % (triggers_header,))
                                if self.ruler:
                                        self.stdout.write("%s\n"%str(self.ruler * len(triggers_header)))
                                self.columnize([r'\r',], maxcol-1)
                                self.stdout.write("\n")

        def do_help(self, arg):
                """Overridden Cmd.do_help so we can allow \ prefixed
                special comands to be looked up.
                """
                if arg in (r'\r', 'r',):
                        print >> sys.stdout, "<query>\\r\nQuery trigger to clear the query buffer\nfrom within a query, e.g.:\n\n" + \
                              "SELECT * FROM the_wrong_table WHERE \\r\n\n..will not execute."
                else:
                        return cmd.Cmd.do_help(self, re.sub(self.special_cmds_re, r'\1', arg))

        def do_l(self, line):
                """\l
List schemas
"""
                if not self.current:
                        print_table(self.get_schemas(), self.vertical_display)

        def do_d(self, line):
                """Method to handle special comand \d,
to list tables or columnds in a table if line isn't empty.
"""
                if not self.current:
                        if line.strip():
                                print_table(self.get_columns(line), self.vertical_display)
                        else:
                                print_table(self.get_tables(), self.vertical_display)

        def do_c(self, line):
                """\c <schema>
Change current connection to another template or profile.
"""
                if not self.current and self.connect(line.strip()):
                        print >> sys.stdout, "Connected to '%s'" % (line.strip(),)
                        self.data_cache = {}


        def do_G(self, line):
                """\G
Toggles vertical display mode on/off.
"""
                if self.vertical_display:
                        print >> sys.stdout, 'Vertical results mode OFF'
                        self.vertical_display = False
                else:
                        print >> sys.stdout, 'Vertical results mode ON'
                        self.vertical_display = True

        def do_x(self, line):
                """\\x
Alias of \G.
"""
                return self.do_G(line)

        def default(self, line):
                """Method to handle unhandled comands, will treat
                line as SQL. If the escape character ';' is not present,
                line is appended to self.current and not run until the
                character is present.
                """
                # Handle control char ^D as an exit command
                if self.current == '' and line.rstrip() == '\x04':
                        self.do_exit(None)

                # Handle query buffer reset
                if line.rstrip().endswith(r'\r'):
                        self.current = ''
                        self.prompt = self._prompt
                        print >> sys.stdout, "Query buffer reset (cleared)."
                else:
                        self.current = '%s %s' % (self.current, line,)

                        if ';' in self.current:
                                first = True
                                data = []
                                for row in self.get_query(self.current):
                                        if first:
                                                keys = getattr(row, 'keys', None)
                                                if not keys:
                                                        # If this DBAPI doesn't provide a keys(), then
                                                        # try cursor.description
                                                        keys = []
                                                        if hasattr(row, 'cursor'):
                                                                description = getattr(row, 'cursor').description
                                                        else:
                                                                description = getattr(row, 'cursor_description')
                                                        for r in description:
                                                                keys.append(r[0])
                                                else:
                                                        keys = keys()
                                                data.append(keys)
                                                first = False
                                        data.append([v for v in row])
                                if len(data) > 1:
                                        print_table(data, self.vertical_display)
                                        print >> sys.stdout, "\n%d found." % (len(data)-1,)
                                else:
                                        print >> sys.stdout, "\nNo results found."
                                self.current = ''
                                if self.prompt == self.multi_prompt:
                                        self.prompt = self._prompt
                        else:
                                self._prompt = self.prompt
                                self.prompt = self.multi_prompt

        def do_EOF(self, line):
                print >> sys.stdout, "\n%s\n" % (self.outro,)
                return True

        def do_exit(self, line):
                """exit
Does what it says on the tin.
"""
                sys.exit(0);

        def do_clear(self, line):
                """clear
Clear cache of profiles, templates, tables and table columns.
"""
                self.data_cache = {}
                print >> sys.stdout, "Cache cleared."

        def get_query(self, sql):
                """Helper method to get results for an SQL
                query, via the internal DBAPI cursor.
                """
                try:
                        data = self.cursor.execute(sql).fetchall()
                except Exception, e:
                        data = tuple()
                        error(e, False)
                return data

        def get_schemas(self, profile_id):
                """Helper method to get a list of available schemas/DBs.
                """
                raise NotImplementedError

        def get_tables(self):
                """Helper method to return a list of tables
                for the current schema, from the internal
                DBAPI cursor.
                """
                raise NotImplementedError

        def get_columns(self, table):
                """Helper method to return a list of column metadata
                for a given table.
                """
                raise NotImplementedError

        def connect(self, dsn):
                """Perform connection to another DB and set cursor(s).
                """
                raise NotImplementedError

        @property
        def special_cmds_re(self):
            return re.compile('^[\\\\]([%s])(\\s|$)(.*)' % (''.join(self.special_cmds),))

        @property
        def unesc_special_cmds_re(self):
            return re.compile('^([%s])(\\s|$)(.*)' % (''.join(self.special_cmds),))
