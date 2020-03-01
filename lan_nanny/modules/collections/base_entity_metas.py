"""Base Entity Metas Collection

"""
from .base import Base

class BaseEntityMetas(Base):

    def __init__(self, conn=None, cursor=None):
        """Base collection constructor. var `table_name must be the """
        super(BaseEntityMetas, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor

        self.table_name = None
        self.collect_model = None

    def get_all(self) -> list:
        """Get all of a models instances from the database."""
        pretties = super().get_all()

        for pretty in pretties:

        return pretties


# End File: lan-nanny/lan_nanny/modules/collections/base_entity_metas.py
