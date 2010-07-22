pyDBCLI is a package for creating interactive command line database query tools, using Python's ``cmd.Cmd``, similar to tools like ``psql`` and ``mysql``.


Requirements
============

pyDBCLI itself just needs ``cmd`` to be present, so as long as you've got Python >=1.4, you're good.

The *odbc* extra requires PyODBC >=2.0.


Installation
============

Install ``pyDBCLI`` using easy_install::

    easy_install pyDBCLI

Or from the setup script::

    python setup.py install


Usage
=====

For the most part you can drop ``pyDBCLI.utils.Utility`` in place of ``cmd.Cmd``, with a few extra properties, e.g.

*multi_prompt*
  What you want the *prompt* to be replaced with when in the middle of a multi-line SQL statement.

*cursor*
  DBAPI cursor to use to run queries, this should be set on the **instance** of the Utility rather than in the class definition.

*system_cursor*
  Same as *cursor* but used for non-schema specific queries, e.g. display lists of schemas and other metadata.

*special_cmds*
  List/tuple of "escaped" commands, e.g. those beginning with ``\``, such as ``\d``. This can be overridden in the class definition, but as you probably don't want to clear the existing set of commands, you can instead add to this list in your constructor::

    def __init__(self, *args, **kwargs):
        Utility.__init__(self, *args, **kwargs)
	self.special_cmds.append('foo')
	self.special_cmds.append('bar')

*data_cache*
  Used for caching metadata, such as lists of schemas, and tables. If you redefine this, use something that implements ``UserDict`` or uses the ``DictMixin``, as ``pyDBCLI.helpers.memoized`` expects a dict like instance.

*db_types*
  Dict of Python type classes (as returned by DBAPI cursors) to appropriate SQL type strings.

The only methods not fully implemented by ``Utility`` are:

- get_schemas
- get_tables
- get_columns
- connect

As these can all be done in different ways depeneding on the DBAPI compliant library used to connect to the database being queried.

You can also, as with ``cmd.Cmd`` add your own commands handles (e.g. ``def do_mycommand``), or override any existing commands if you need to.

Some helper methods are provided by ``pyDBCLI.helpers``, specifically a method to pretty print tabular data, a memoize decorator that targets the *data_cache* property of ``Utility``, and some CLI helpers for printing usage and handling errors.
