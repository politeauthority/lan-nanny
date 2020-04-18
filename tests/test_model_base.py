"""Test Base Model

"""
from datetime import datetime
from dateutil.tz import tzutc
import os

import arrow
import pytest

from lan_nanny.modules import db
from lan_nanny.modules.models.base import Base

from .configs import CONFIGS

test_db = os.path.join(CONFIGS['tmp_dir'], 'test.db')
if os.path.exists(test_db):
    os.remove(test_db)
conn, cursor = db.create_connection(test_db)


GENERIC_FIELDS = [
    {
        'name': 'field_three',
        'type': 'bool',
        'default': False
    },
    {
        'name': 'field_four',
        'type': 'str',
        'default': 'test'
    },
    {
        'name': 'field_five',
        'type': 'int',
        'default': 7
    },
    {
        'name': 'field_six',
        'type': 'datetime',
    },
    {
        'name': 'field_seven',
        'type': 'bool',
    }]


class TestModelBase():

    def test___init__(self):
        """
        Tests the Base.__init__ method.

        """
        base = Base(conn, cursor)
        assert base.conn == conn
        assert base.cursor == cursor
        assert base.iodku
        assert not base.table_name
        assert base.base_map == [
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
        assert base.field_map == []

    def test__create_total_map(self):
        """
        Tests the _create_total_map function to verify it's properly adding self.base_map and
        self.field_map class vars to create self.total_map.

        """
        base = Base()
        base.field_map = [
            {
                'name': 'field_two',
                'type': 'str',
            }]
        base._create_total_map()
        assert base.total_map == [
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
                'name': 'field_two',
                'type': 'str',
            }
        ]

    def test_set_defaults(self):
        """
        Tests the _set_defaults method, making sure we set the default values for fields in the
        field map on the class.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base._create_total_map()
        assert base._set_defaults()
        assert base.field_three == False
        assert base.field_four == 'test'
        assert base.field_five == 7

    def test_set_types(self):
        """
        Tests the _set_types method, making sure we set the correct types for each type.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base._create_total_map()
        base._set_defaults()
        base.field_three = 1
        base.field_five = '5'
        base.field_six = datetime(2020, 1, 1)
        base.field_seven = 0

        # check that ints and bools are converted where possible.
        base._set_types()
        assert base.field_three == True
        assert base.field_five == 5
        assert base.field_seven == False
        # assert type(base.field_six) == 'datetime'

        base.field_five = 'five'
        with pytest.raises(AttributeError):
            base._set_types()

        # reset field_five, set field_seven to string 0 to see if it converts to negative bool
        base.field_three = 'True'
        base.field_five = 5
        base.field_seven = 'false'
        base._set_types()
        assert base.field_three
        assert base.field_seven == False

    def test__convert_bools(self):
        """
        Tests the _convert_bool method to make sure we translate accepted values to bool.

        """
        base = Base()
        assert base._convert_bools('test_int_1', 1) == True
        assert base._convert_bools('test_str_1', '1')
        assert base._convert_bools('test_int_1_false', 0) == False
        assert base._convert_bools('test_str_1_false', '0') == False
        assert base._convert_bools('test_str_2_false', 'false') == False

        # @todo fix this
        # with pytest.raises(AttributeError):
        #     base._convert_bools('test_str_3_false', '5')

    def test__convert_ints(self):
        """
        Tests the _convert_int method to make sure we translate accepted values.
        """
        base = Base()
        assert base._convert_ints('test_int_1', 1) == 1
        assert base._convert_ints('test_str_1', '1') == 1
        assert base._convert_ints('test_int_1_false', 0) == 0
        assert base._convert_ints('test_str_1_false', '0') == 0
        with pytest.raises(AttributeError):
            assert base._convert_ints('test_str_2_false', 'false') == False

    def test__generate_create_table_feilds(self):
        """
        Tests the _generate_create_table_feilds method to make sure it creates the sql needed to
        create custom fields.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base.setup()
        generated_fields = base._generate_create_table_feilds()
        fields = """id INTEGER PRIMARY KEY AUTOINCREMENT,
created_ts DATE,
field_three INTEGER,
field_four TEXT DEFAULT test,
field_five INTEGER DEFAULT 7,
field_six DATE,
field_seven INTEGER"""
        assert generated_fields == fields

    def test__xlate_field_type(self):
        """
        Tests the _xlate_field_type method to make sure we turn python types to sql lite types.

        """
        base = Base()
        assert base._xlate_field_type('int') == 'INTEGER'
        assert base._xlate_field_type('datetime') == 'DATE'
        assert base._xlate_field_type('str') == 'TEXT'
        assert base._xlate_field_type('bool') == 'INTEGER'

    def test_build_from_list(self):
        """
        Tests the build_from_list method to make sure it builds out the class.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base.setup()

        sql_ret = [
            1,                               # id
            datetime(2020, 1, 8, 5, 1, 48),  # created_ts
            1,                               # field_three
            'TEST',                          # field_four
            5,                               # field_five
            datetime(2020, 1, 8, 5, 1, 48),  # field_six
            0]                               # field_seven
        base.build_from_list(sql_ret)
        assert base.id == 1
        assert base.created_ts == datetime(2020, 1, 8, 5, 1, 48, tzinfo=tzutc())
        assert base.field_three == True
        assert base.field_four == 'TEST'
        assert base.field_five == 5
        assert base.field_six == datetime(2020, 1, 8, 5, 1, 48, tzinfo=tzutc())
        assert base.field_seven == 0

    def test_check_required_class_vars(self):
        """
        Tests the check_required_class_vars to make sure we're requiring the right class vars or
        throwing an AttributeError.

        """
        base = Base(conn, cursor)
        base.field_map = GENERIC_FIELDS
        base.setup()
        base.check_required_class_vars()
        with pytest.raises(AttributeError):
            base.check_required_class_vars(['test'])

    def test_get_update_set_sql(self):
        """
        Tests the get_update_set_sql method to make sure it creates the correct SET pairs for an
        update.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base.setup()
        generated_set = base.get_update_set_sql()
        updated_set = """created_ts = ?,
field_three = ?,
field_four = ?,
field_five = ?,
field_six = ?,
field_seven = ?"""
        assert generated_set == updated_set

    def test_get_parmaterized_num(self):
        """
        Tests the get_parmaterized_num method to make sure it supplies the right amount of
        parameterized values.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base.setup()
        param_str = base.get_parmaterized_num()
        assert param_str == "?, ?, ?, ?, ?, ?"
        param_str = base.get_parmaterized_num(['id', 'field_three'])
        assert param_str == "?, ?, ?, ?, ?"

    def test_get_values_sql(self):
        """
        Tests the get_values_sql method to make sure its grabbing the right values to send the the
        db.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base.setup()
        base.field_three = True
        base.field_four = 'testing'
        base.field_five = 5
        base.field_six = datetime(2020, 1, 1)
        base.field_seven = False
        value_tuple = base.get_values_sql()
        assert len(value_tuple) == 6
        assert isinstance(value_tuple[1], int)
        assert value_tuple[2] == 'testing'

    def test_get_fields_sql(self):
        """
        Tests the get_parmaterized_num method to make sure it supplies the right amount of
        parameterized values.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base.setup()
        base.field_three = True
        base.field_four = 'testing'
        base.field_five = 5
        base.field_six = datetime(2020, 1, 1)
        base.field_seven = False
        field_sql = base.get_fields_sql()
        assert field_sql == \
            'created_ts, field_three, field_four, field_five, field_six, field_seven'

    def test_create_table(self):
        """
        Tests the create_table method making sure it can actually make a table.

        """
        base = Base(conn, cursor)
        base.field_map = GENERIC_FIELDS
        base.table_name = 'test_table'
        base.setup()
        base.create_table()
        assert self.get_table(base.table_name)

    def test_insert(self):
        """
        Tests the insert method making sure it can actually make a table.

        """
        base = Base(conn, cursor)
        base.field_map = GENERIC_FIELDS
        base.table_name = 'test_table'
        base.setup()
        base.field_three = True
        base.field_four = 'test'
        base.field_five = 8
        base.field_six = datetime(2020, 1, 1)
        base.field_seven = False
        base.insert()
        data = self.get_data('test_table')
        assert len(data) == 1
        assert isinstance(arrow.get(data[0][1]).datetime, datetime)

    def test_get_by_id(self):
        """
        """
        base = Base(conn, cursor)
        base.field_map = GENERIC_FIELDS
        base.table_name = 'test_table'
        base.setup()
        base.get_by_id(1)
        assert base.id == 1

    def test_save(self):
        """
        Tests the save method making sure it can actually make a table.

        """
        base = Base(conn, cursor)
        base.field_map = GENERIC_FIELDS
        base.table_name = 'test_table'
        base.setup()
        base.get_by_id(1)
        base.field_three = False
        base.field_four = 'testy'
        base.field_five = 9
        base.save()
        data = self.get_data('test_table')[0]
        assert data[2] == 0
        assert data[3] == 'testy'
        assert data[4] == 9

    def get_table(self, table_name: str):
        sql = """
            SELECT
                name
            FROM
                sqlite_master
            WHERE
                type ='table' AND
                name='%s';""" % table_name
        cursor.execute(sql)
        table = cursor.fetchone()
        if table_name in table:
            return True
        return False

    def get_data(self, table_name: str):
        """
        Gets data from the sql lite box.

        """
        sql = "SELECT * FROM %s;" % table_name
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    @classmethod
    def teardown_class(cls):
        """
        Tears down the sqlite database after tests finish.

        """
        os.remove(test_db)

# EndFile: lan-nanny/tests/test_model_base.py
