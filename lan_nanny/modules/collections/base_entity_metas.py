"""Base Entity Metas Collection
This class should be extended by all collections that collect models that have entity meta.

"""
from .base import Base
from ..models.entity_meta import EntityMeta

class BaseEntityMetas(Base):

    def __init__(self, conn=None, cursor=None):
        """Base collection constructor. var `table_name must be the """
        super(BaseEntityMetas, self).__init__(conn, cursor)
        self.table_name = None
        self.collect_model = None
        self.meta_table = 'entity_metas'

    def get_with_meta_value(self, meta_name: str, meta_value) -> list:
        """Collect models with a meta key and value."""
        sql = """
            SELECT *
            FROM %s
            WHERE
                entity_type = "%s" AND
                name = "%s" AND
                value = "%s"
        """ % (self.meta_table, self.table_name, meta_name, meta_value)
        self.cursor.execute(sql)
        metas_raw = self.cursor.fetchall()
        prestines = []
        for meta_raw in metas_raw:
            meta = EntityMeta(self.conn, self.cursor)
            meta.build_from_list(meta_raw)
            model = self.collect_model(self.conn, self.cursor)
            model.get_by_id(meta.entity_id)
            prestines.append(model)
        return prestines


# End File: lan-nanny/lan_nanny/modules/collections/base_entity_metas.py
