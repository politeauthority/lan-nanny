"""Test Base Model

"""
from datetime import datetime

import pytest

from lan_nanny.modules import db
from lan_nanny.modules.models.base import Base

conn, cursor = db.create_connection('test.db')


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
    },]


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
        Tests the convert_bool method to make sure we translate accepted values to bool.

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

    def test__generate_create_table_feilds(self):
        """
        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base._generate_create_table_feilds()

    def test_build_from_list(self):
        """
        Tests the build_from_list method to make sure it builds out the class.

        """
        base = Base()
        base.field_map = GENERIC_FIELDS
        base.setup()

        sql_ret = [
            1,                              # id
            datetime(2020, 1, 8, 5, 1, 48), # created_ts
            1,                              # field_three
            'TEST',                         # field_four
            5,                              # field_five
            datetime(2020, 1, 8, 5, 1, 48), # field_six
            0]                              # field_seven
        base.build_from_list(sql_ret)
        assert base.id == 1
        assert base.created_ts == datetime(2020, 1, 8, 5, 1, 48)
        assert base.field_three == True
        assert base.field_four == 'TEST'
        assert base.field_five == 5
        assert base.field_six == datetime(2020, 1, 8, 5, 1, 48)
        assert base.field_seven == 0


if __name__ == '__main__':
    base = Base()
    base._convert_bools('test_str_3_false', '5')
    base = Base()
    base.field_map = GENERIC_FIELDS
    x = base._generate_create_table_feilds()

    print(x)
    import ipdb; ipdb.set_trace()


# EndFile: lan-nanny/tests/test_model_base.py