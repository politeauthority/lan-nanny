"""Entity Meta Model

"""
import logging

from .base import Base


class EntityMeta(Base):

    def __init__(self, conn=None, cursor=None):
        super(EntityMeta, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = 'entity_metas'
        self.field_map = [
            {
                'name': 'update_ts',
                'type': 'datetime'
            },
            {
                'name': 'entity_type',
                'type': 'str',
            },
            {
                'name': 'entity_id',
                'type': 'int',
            },
            {
                'name': 'name',
                'type': 'str',
            },
            {
                'name': 'type',
                'type': 'str'
            },
            {
                'name': 'value',
                'type': 'str'
            },
        ]
        self.setup()

    def __repr__(self):
        return "<EntityMeta %s %s:%s>" % (self.entity_type, self.name, self.value)

    def build_from_list(self, raw: list):
        """
        Build a model from an ordered list, converting data types to their desired type where
        possible.

        """
        count = 0
        for field in self.total_map:
            setattr(self, field['name'], raw[count])
            count += 1
            if self.type == 'bool':
                self.value = self._set_bool(self.value)

        return True

    def _set_bool(self, value) -> bool:
        """Set a boolean option to the correct value."""
        value = str(value).lower()
        # Try to convert values to the positive.
        if value == '1' or value == 'true':
            return True
        # Try to convert values to the negative.
        elif value == '0' or value == 'false':
            return False

# End File: lan-nanny/lan_nanny/modules/models/entity_meta.py
