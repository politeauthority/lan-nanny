"""Base Model
Parent class for all models to inherit, providing methods for creating tables, inserting, updating,
selecting and deleting data.

The Base Model SQL driver can work with both SQLite3 and MySQL database.
    self.backend = "sqlite" for SQLite3
    self.backend = "mysql" for MySQL

"""
from datetime import datetime
import logging
from sqlite3 import Error

import arrow


class Base:

    def __init__(self, conn=None, cursor=None):
        """Base model constructor
        """
        self.conn = conn
        self.cursor = cursor
        self.iodku = True
        self.backend = "mysql"

        self.table_name = None
        self.base_map = [
            {
                'name': 'id',
                'type': 'int',
                'primary': True,
            },
            {
                'name': 'created_ts',
                'type': 'datetime',
            },
            {
                'name': 'updated_ts',
                'type': 'datetime',
            }
        ]
        self.field_map = []
        self.setup()

    def __repr__(self):
        if self.id:
            return "<%s: %s>" % (self.__class__.__name__, self.id)
        return "<%s>" % self.__class__.__name__

    def connect(self, conn, cursor):
        """Quick bootstrap method to connect the model to the database connection. """
        self.conn = conn
        self.cursor = cursor
        return True

    def create_table(self) -> bool:
        """Create a table based on the self.table_name, and self.field_map. """
        logging.debug('Creating %s' % self.__class__.__name__)
        self._create_total_map()
        if not self.table_name:
            raise AttributeError('Model table name not set, (self.table_name)')
        sql = "CREATE TABLE IF NOT EXISTS %s \n(%s)" % (
            self.table_name,
            self._generate_create_table_feilds())
        logging.debug('Creating table: %s' % self.table_name)
        logging.debug(sql)
        try:
            self.cursor.execute(sql)
            return True
        except Error as e:
            logging.error(e)
        return False

    def setup(self) -> bool:
        """Set up model class vars, sets class var defaults, and corrects types where possible."""
        self._create_total_map()
        self._set_defaults()
        self._set_types()
        return True

    def insert(self):
        """Insert a new record of the model. """
        self.setup()
        self.check_required_class_vars()

        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime

        insert_sql = "INSERT INTO %s (%s) VALUES (%s)" % (
            self.table_name,
            self.get_fields_sql(skip_fields=['id']),
            self.get_parmaterized_num())
        print(insert_sql)
        print(self.get_values_sql(skip_fields=['id']))
        self.cursor.execute(insert_sql, self.get_values_sql(skip_fields=['id']))

        self.conn.commit()
        self.id = self.cursor.lastrowid
        return True

    def save(self, where: list = []) -> bool:
        """Saves a model instance in the model table. """
        self.setup()
        self.check_required_class_vars()

        if self.iodku and not self.id:
            return self.insert()
        if not self.id and not where:
            raise AttributeError('Save failed, missing self.id or where list')

        where_sql = "id = %s" % self.id
        if where:
            where_sql = "%s = %s" % (where[0], where[1])

        update_sql = """
            UPDATE %s
            SET
            %s
            WHERE
            %s""" % (
            self.table_name,
            self.get_update_set_sql(),
            where_sql)
        self.cursor.execute(update_sql, self.get_values_sql())
        self.conn.commit()
        return True

    def delete(self) -> bool:
        """Delete a model item."""
        sql = """DELETE FROM %s WHERE id = %s """ % (self.table_name, self.id)
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def get_by_id(self, model_id: int = None) -> bool:
        """Get a single model object from db based on an object ID."""
        if model_id:
            self.id = model_id
        elif not self.id:
            AttributeError('%s is missing an id attribute.' % __class__.__name__)
        sql = """
            SELECT *
            FROM %s
            WHERE id = %s""" % (self.table_name, self.id)
        self.cursor.execute(sql)
        raw = self.cursor.fetchone()
        if not raw:
            return False

        self.build_from_list(raw)

        return True

    def get_last(self) -> bool:
        """Get the last created model."""
        sql = """
            SELECT *
            FROM %s
            ORDER BY created_ts DESC
            LIMIT 1""" % (self.table_name)

        self.cursor.execute(sql)
        run_raw = self.cursor.fetchone()
        if not run_raw:
            return False
        self.build_from_list(run_raw)
        return True

    def build_from_list(self, raw: list) -> bool:
        """Build a model from an ordered list, converting data types to their desired type where 
           possible.
           :param raw: The raw data from the database to be converted to model data.
        """
        count = 0
        for field in self.total_map:
            field_name = field['name']
            field_value = raw[count]

            # Handle the bool field type.
            if field['type'] == 'bool':
                if field_value == 1:
                    setattr(self, field_name, True)
                elif field_value == 0:
                    setattr(self, field_name, False)
                else:
                    setattr(self, field_name, None)

            # Handle the datetime field type.
            elif field['type'] == 'datetime':
                if field_value:
                    setattr(self, field_name, arrow.get(field_value).datetime)
                else:
                    setattr(self, field_name, None)

            # Handle all other field types without any translation.
            else:
                setattr(self, field_name, field_value)

            count += 1

        return True

    def get_fields_sql(self, skip_fields: list = ['id']) -> str:
        """Get all class table column fields in a comma separated list for sql cmds. """
        field_sql = ""
        for field in self.total_map:
            # Skip fields we don't want included in db writes
            if field['name'] in skip_fields:
                continue
            field_sql += "`%s`, " % field['name']
        return field_sql[:-2]

    def get_parmaterized_num(self, skip_fields: list = ['id']) -> str:
        """Generates the number of parameterized "?" for the sql lite parameterization."""
        field_value_param_sql = ""
        for field in self.total_map:

            # Skip fields we don't want included in db writes
            if field['name'] in skip_fields:
                continue

            # MySQL and SQLite has different substitution phrases for parameterized queries.
            if self.backend == "mysql":
                subsitution_phrase = "%s"
            else:
                subsitution_phrase = "?"

            field_value_param_sql += "%s, " % subsitution_phrase

        field_value_param_sql = field_value_param_sql[:-2]
        return field_value_param_sql

    def get_values_sql(self, skip_fields: list = ['id', 'created_ts']) -> tuple:
        """Generate the model values to send to the sql lite interpretor as a tuple. """
        vals = []
        for field in self.total_map:
            # Skip fields we don't want included in db writes
            if field['name'] in skip_fields:
                continue

            field_value = getattr(self, field['name'])

            # SQLite doesn't support bools, so we update them to ints before saving.
            if field['type'] == 'bool':
                if field_value == False:
                    field_value = 0
                    vals.append(field_value)
                    continue
                elif not field_value:
                    field_value = None
                    vals.append(field_value)
                    continue

                if field_value:
                    field_value = 1
                elif field_value == False:
                    field_value = 0
                else:
                    raise AttributeError('Model %s var self.%s with type bool has value of %s' % (
                        __class__.__name__,
                        field['name'],
                        field_value))

            if field['name'] == 'update_ts' and field['type'] == 'datetime' and not self.update_ts:
                self.update_ts = arrow.utcnow().datetime
                field_value = self.update_ts

            vals.append(field_value)

        return tuple(vals)

    def get_update_set_sql(self, skip_fields=['id', 'created_ts']):
        """Generate the models SET sql statements, ie: SET key = value, other_key = other_value. """
        set_sql = ""
        for field in self.total_map:
            if field['name'] in skip_fields:
                continue
            set_sql += "`%s` = ?,\n" % field['name']
        if self.backend == "mysql":
            set_sql = set_sql.replace("?", "%s")
        return set_sql[:-2]

    def check_required_class_vars(self, extra_class_vars: list = []) -> bool:
        """Quick class var checks to make sure the required class vars are set before proceeding
           with an operation.
        """
        if not self.conn:
            raise AttributeError('Missing self.conn')

        if not self.cursor:
            raise AttributeError('Missing self.cursor')

        if not self.total_map:
            raise AttributeError('Missing self.total_map')

        for class_var in extra_class_vars:
            if not getattr(self, class_var):
                raise AttributeError('Missing self.%s' % class_var)

        return True

    def _create_total_map(self) -> bool:
        """Concatenate the base_map and models field_map together into self.total_map. """
        self.total_map = self.base_map + self.field_map
        return True

    def _set_defaults(self) -> bool:
        """Set the defaults for the class field vars and populates the self.field_list var
           containing all table field names.
        """
        self.field_list = []
        for field in self.total_map:
            field_name = field['name']
            self.field_list.append(field_name)

            default = None
            if 'default' in field:
                default = field['default']

            # Sets all class field vars with defaults.
            field_value = getattr(self, field_name, None)
            if not field_value and field_value != False:
                setattr(self, field_name, default)

        return True

    def _set_types(self) -> bool:
        """Set the types of class table field vars and corrects their types where possible."""
        for field in self.total_map:
            class_var_name = field['name']

            class_var_value = getattr(self, class_var_name)
            if class_var_value == None:
                continue

            if field['type'] == 'int' and type(class_var_value) != int:
                converted_value = self._convert_ints(class_var_name, class_var_value)
                setattr(self, class_var_name, converted_value)
                continue

            # if field['type'] == 'bool':
            #     converted_value = self._convert_bools(class_var_name, class_var_value)
            #     setattr(self, class_var_name, converted_value)
            #     continue

            if field['type'] == 'datetime' and type(class_var_value) != datetime:
                print(field)
                setattr(
                    self,
                    class_var_name,
                    arrow.get(class_var_value).datetime)
                continue

    def _convert_ints(self, name: str, value) -> bool:
        """Attempts to convert ints to a usable value or raises an AttributeError. """
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            logging.warning('Class %s field %s value %s is not int, changed to int.' % (
                __class__.__name__, name, value))
            return int(value)
        raise AttributeError('Class %s field %s value %s is not int.' % (
            __class__.__name__, name, value))

    def _convert_bools(self, name: str, value) -> bool:
        """Convert bools into usable value or raises an AttributeError. """
        if isinstance(value, bool):
            return value

        if value == None:
            return None

        value = str(value).lower()
        # Try to convert values to the positive.
        if value == '1' or value == 'true':
            return True
        # Try to convert values to the negative.
        elif value == '0' or value == 'false':
            return False
        else:
            AttributeError('%s field %s should be type bool.' % (
                __class__.__name__, name))
            logging.error('%s field %s should be type bool.' % (
                __class__.__name__, name))

    def _generate_create_table_feilds(self) -> str:
        """Generates all fields column create sql statements."""
        field_sql = ""
        field_num = len(self.total_map)
        c = 1
        for field in self.total_map:
            primary_stmt = ''
            if 'primary' in field and field['primary']:
                primary_stmt = ' PRIMARY KEY'
                if self.backend == "mysql":
                    primary_stmt += ' AUTO_INCREMENT'

            not_null_stmt = ''
            if 'not_null' in field and field['not_null']:
                not_null_stmt = ' NOT NULL'

            default_stmt = ''
            if 'default' in field and field['default']:
                if field['type'] == "str":
                    default_stmt = ' DEFAULT "%s"' % field['default']
                else:
                    default_stmt = ' DEFAULT %s' % field['default']

            field_line = "`%(name)s` %(type)s%(primary_stmt)s%(not_null_stmt)s%(default_stmt)s," % {
                'name': field['name'],
                'type': self._xlate_field_type(field['type']),
                'primary_stmt': primary_stmt,
                'not_null_stmt': not_null_stmt,
                'default_stmt': default_stmt
            }
            field_sql += field_line

            if c == field_num:
                field_sql = field_sql[:-1]
            field_sql += "\n"
            c += 1
        field_sql = field_sql[:-1]
        return field_sql

    def _xlate_field_type(self, field_type):
        """Translates field types into sql lite column types.
           @todo: create better class var for xlate map.
        """
        if field_type == 'int':
            return 'INTEGER'
        elif field_type == 'datetime':
            return 'DATETIME'
        elif field_type[:3] == 'str':
            return 'VARCHAR(200)'
        elif field_type == 'bool':
            return 'BOOLEAN'
        elif field_type == 'float':
            return 'DECIMAL(10, 5)'

# End File: lan-nanny/lan_nanny/modules/models/base.py
