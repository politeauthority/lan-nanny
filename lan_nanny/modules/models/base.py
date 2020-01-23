"""Base Model
Parent class for all models to inherit, providing methods for creating tables, inserting, updating,
selecting and deleting data.

"""
from datetime import datetime
import logging
from sqlite3 import Error

import arrow


class Base():

    def __init__(self, conn=None, cursor=None):
        """
        Base model constructor
        @unit-tested

        """
        self.conn = conn
        self.cursor = cursor
        self.iodku = True

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
            }
        ]
        self.field_map = []
        self.setup()

    def __repr__(self):
        if self.id:
            return "<%s: %s>" % (__class__.__name__, self.id)
        return "<%s>" % self.__class__.__name__

    def create_table(self) -> bool:
        """
        Creates a table based on the self.table_name, and self.field_map.
        @unit-tested

        """
        print('Creating %s' % self.__class__.__name__)
        self._create_total_map()
        if not self.table_name:
            raise AttributeError('Model table name not set, (self.table_name)')
        sql = "CREATE TABLE IF NOT EXISTS %s \n(%s)" % (
            self.table_name,
            self._generate_create_table_feilds())
        try:
            self.cursor.execute(sql)
            return True
        except Error as e:
            print(e)
        print(sql)
        return False

    def setup(self):
        """
        Sets up model class vars, sets class var defaults, and corrects types where possible.

        """
        self._create_total_map()
        self._set_defaults()
        self._set_types()

    def insert(self):
        """
        Inserts a new record of the model.
        @unit-tested

        """
        self.setup()
        self.check_required_class_vars()

        if not self.created_ts:
            self.created_ts = arrow.utcnow().datetime

        insert_sql = "INSERT INTO %s (%s) VALUES (%s)" % (
            self.table_name,
            self.get_fields_sql(),
            self.get_parmaterized_num())
        self.cursor.execute(insert_sql, self.get_values_sql())
        self.conn.commit()
        self.id = self.cursor.lastrowid
        return True

    def save(self, where: list = []) -> bool:
        """
        Saves a model instance in the model table.
        @unit-tested

        """
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
        logging.debug(update_sql)
        logging.debug(self.get_values_sql())
        self.cursor.execute(update_sql, self.get_values_sql())
        self.conn.commit()
        return True

    def delete(self, _id: int = None):
        """
        Deletes a model item by id.

        """
        self.setup()
        if _id:
            self.id = _id
        sql = """DELETE FROM %s WHERE id = %s """ % (self.table_name, self.id)
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def get_by_id(self, model_id: int = None) -> bool:
        """
        Gets an alert from the `alerts` table based on it's alert ID.

        """
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

    def build_from_list(self, raw: list):
        """
        Builds a model from an ordered list, converting data types to their desired type where
        possible.
        @unit-tested *
            # elif field['type'] == 'bool':
            #     if raw[count] == 1:
            #         setattr(self, field['name'], True)
            #     else:
            #         setattr(self, field['name'], False)
            # else:
            #     setattr(self, field['name'], raw[count])
        """
        count = 0

        for field in self.total_map:
            if field['type'] == 'datetime':
                setattr(self, field['name'], arrow.get(raw[count]).datetime)
            else:
                setattr(self, field['name'], raw[count])

            count += 1
        return True

    def get_fields_sql(self, skip_fields: list = ['id']) -> str:
        """
        Gets all class table column fields in a comma separated list for sql cmds.
        @unit-tested

        """
        field_sql = ""
        for field in self.total_map:
            # Skip fields we don't want included in db writes
            if field['name'] in skip_fields:
                continue
            field_sql += "%s, " % field['name']
        return field_sql[:-2]

    def get_parmaterized_num(self, skip_fields: list = ['id']) -> str:
        """
        Generates the number of parameterized "?" for the sql lite parameterization.
        @unit-tested

        """
        field_value_param_sql = ""
        for field in self.total_map:

            # Skip fields we don't want included in db writes
            if field['name'] in skip_fields:
                continue

            field_value_param_sql += "?, "

        field_value_param_sql = field_value_param_sql[:-2]
        return field_value_param_sql

    def get_values_sql(self, skip_fields: list = ['id']) -> tuple:
        """
        Generates the model values to send to the sql lite interpretor as a tuple.
        @unit-tested

        """
        vals = []
        for field in self.total_map:
            # Skip fields we don't want included in db writes
            if field['name'] in skip_fields:
                continue

            field_value = getattr(self, field['name'])

            # SQLite doesnt support bools, so we update them to ints before saving.
            if field['type'] == 'bool':
                if field_value == False:
                    field_value = 0
                    vals.append(field_value)
                    continue
                elif not field_value:
                    field_value = "NULL"
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

    def get_update_set_sql(self, skip_fields=['id']):
        """
        Generates the models SET sql statements, ie: SET key = value, other_key = other_value.
        @unit-tested - @todo needs updating for "skip_fields"

        """
        set_sql = ""
        for field in self.total_map:
            if field['name'] in skip_fields:
                continue
            set_sql += "%s = ?,\n" % field['name']
        return set_sql[:-2]

    def check_required_class_vars(self, extra_class_vars: list = []):
        """
        Quick class var checks to make sure the required class vars are set before proceeding with
        an operation.
        @unit-tested

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

    def _create_total_map(self) -> bool:
        """
        Slams the base_map and models field_map together into self.total_map.
        @unit-tested

        """
        self.total_map = self.base_map + self.field_map
        return True

    def _set_defaults(self) -> bool:
        """
        Sets the defaults for the class field vars and populates the self.field_list var containing
        all table field names.
        @unit-tested

        """
        self.field_list = []

        for field in self.total_map:
            name = field['name']
            default = None
            if 'default' in field:
                default = field['default']
            self.field_list.append(name)

            # Sets all class field vars with defaults.
            if not getattr(self, name, None):
                setattr(self, name, default)
        return True

    def _set_types(self) -> bool:
        """
        Sets the types of class table field vars and corrects their types where possible.
        @unit-tested

        """
        for field in self.total_map:
            class_var_name = field['name']
            class_var_value = getattr(self, class_var_name)
            if not class_var_value:
                continue

            if field['type'] == 'int' and type(class_var_value) != int:
                converted_value = self._convert_ints(class_var_name, class_var_value)
                setattr(self, class_var_name, converted_value)
                continue

            if field['type'] == 'bool' and type(class_var_value) != bool:
                converted_value = self._convert_bools(class_var_name, class_var_value)
                setattr(self, class_var_name, converted_value)
                continue

            if field['type'] == 'datetime' and type(class_var_value) != datetime:
                setattr(
                    self,
                    field['name'],
                    arrow.get(class_var_value).datetime)
                continue

    def _convert_ints(self, name: str, value) -> bool:
        """
        Attempts to convert ints to a usable value or raises an AttributeError.
        @unit-tested

        """
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            logging.warning('Class %s field %s value %s is not int, changed to int.' % (
                __class__.__name__, name, value))
            return int(value)
        raise AttributeError('Class %s field %s value %s is not int.' % (
            __class__.__name__, name, value))

    def _convert_bools(self, name: str, value) -> bool:
        """
        Attempts to convert bools into usable value or raises an AttributeError.
        @unit-tested

        """
        if isinstance(value, bool):
            return value

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

    def _generate_create_table_feilds(self) -> str:
        """
        Generates all fields column create sql statements.
        @unit-tested

        """
        field_sql = ""
        field_num = len(self.total_map)
        c = 1
        for field in self.total_map:
            primary_stmt = ''
            if 'primary' in field and field['primary']:
                primary_stmt = ' PRIMARY KEY AUTOINCREMENT'

            not_null_stmt = ''
            if 'not_null' in field and field['not_null']:
                not_null_stmt = ' NOT NULL'

            default_stmt = ''
            if 'default' in field and field['default']:
                default_stmt = ' DEFAULT %s' % field['default']

            field_line = "%(name)s %(type)s%(primary_stmt)s%(not_null_stmt)s%(default_stmt)s," % {
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
        """
        Translates field types into sql lite column types.
        @todo: create better class var for xlate map.
        @unit-tested

        """
        if field_type == 'int':
            return 'INTEGER'
        elif field_type == 'datetime':
            return 'DATE'
        elif field_type == 'str':
            return 'TEXT'
        elif field_type == 'bool':
            return 'INTEGER'

# End File: lan-nanny/modules/models/base.py
