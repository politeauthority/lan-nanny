"""Test Base Model

"""
from lan_nanny.modules import db
from lan_nanny.modules.models.base import Base

conn, cursor = db.create_connection('test.db')


class TestModelBase():


    def test___init__(self):
        """
        Tests the Base.__init__ method.

        """
        base = Base(conn, cursor)
        assert base.conn == conn
        assert base.cursor == cursor
        assert base.iodku
        assert not base.model_name
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
