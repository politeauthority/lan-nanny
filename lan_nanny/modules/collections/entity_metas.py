"""Entity Metas
Gets collections of entity options.

"""
from ..models.entity_meta import EntityMeta


class EntityMetas:

    def __init__(self, conn=None, cursor=None):
        self.conn = conn
        self.cursor = cursor
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
        metas = []
        for raw_meta in raw_metas:
            meta = EntityOption()
            meta.build_from_list(raw_meta)
            metas.append(meta)
        keyed_metas = self._get_keyed(metas)
        return keyed_metas

    def _get_keyed(self, metas: list) -> dict:
        """Key options on their option_name."""
        ret_metas = {}
        for meta in metas:
            ret_metas[meta.name] = meta
        return ret_metas

# End File: lan-nanny/modules/collections/entity_metas.py
