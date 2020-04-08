"""Entity Metas
Gets collections of entity options.

"""
from .base import Base
from ..models.entity_meta import EntityMeta


class EntityMetas(Base):

    def __init__(self, conn=None, cursor=None):
        super(EntityMetas, self).__init__(conn, cursor)
        self.collect_model = EntityMeta
        self.table_name = EntityMeta().table_name

    def get(self, entity_type: str, entity_id: int) -> dict:
        """Get all entity metas for a single entity."""
        sql = """
            SELECT *
            FROM %s
            WHERE
                entity_type=? AND
                entity_id=?;
            """ % self.table_name
        self.cursor.execute(sql(entity_type, entity_id))
        raw_metas = self.cursor.fetchall()
        metas = self.build_from_lists(raw_metas)
        keyed_metas = self._get_keyed(metas)
        return keyed_metas

    def _get_keyed(self, metas: list) -> dict:
        """Key metas on their meta name."""
        ret_metas = {}
        for meta in metas:
            ret_metas[meta.name] = meta
        return ret_metas

# End File: lan-nanny/modules/collections/entity_metas.py
