"""Base Entity Meta Model
Base model class for all models requiring meta storage.

"""
from .base import Base
from .entity_meta import EntityMeta


class BaseEntityMeta(Base):
    def __init__(self, conn=None, cursor=None):
        """Base Entity Meta model constructor."""
        super(BaseEntityMeta, self).__init__(conn, cursor)
        self.conn = conn
        self.cursor = cursor
        self.table_name = None
        self.table_name_meta = EntityMeta().table_name
        self.meta = {}

    def __repr__(self):
        if self.id:
            return "<%s: %s>" % (self.__class__.__name__, self.id)
        return "<%s>" % self.__class__.__name__

    def get_by_id(self, model_id: int = None) -> bool:
        """Get a single model object from db based on an object ID with all meta data loaded into
           self.metas.
        """
        if not super(BaseEntityMeta, self).get_by_id(model_id):
            return False
        self.load_meta(model_id)
        return True

    def build_from_list(self, raw: list, meta=False) -> bool:
        """Build a model from list, and pull its meta data."""
        super(BaseEntityMeta, self).build_from_list(raw)
        if meta:
            self.load_meta(self.id)

    def save(self) -> bool:
        """Extend the Base model save, settings saves for all model self.metas objects."""
        super().save()
        if not self.metas:
            return True

        if not self.id:
            raise AttributeError('Model %s cant save entity metas with out id' % self)
        for meta_name, meta in self.metas.items():
            if not isinstance(meta, EntityMeta):
                raise AttributeError('Entity meta is not an EntityMeta object: %s' % meta)
            meta.entity_type = self.table_name
            meta.entity_id = self.id
            if not meta.type:
                meta.type = 'str'
            meta.save()
            self.metas[meta_name] = meta
        return True

    def delete(self) -> bool:
        """Delete a model item and it's meta."""
        super().delete()
        sql = """
            DELETE FROM %s
            WHERE
                entity_id = %s AND
                entity_type="%s"
            """ % (self.table_name_meta, self.id, self.table_name)
        self.cursor.execute(sql)
        self.conn.commit()
        return True

    def get_meta(self, meta_name: str):
        """Get a meta key from an entity if it exists, or return None. """
        if meta_name not in self.metas:
            return False
        else:
            return self.metas[meta_name]

    def meta_update(self, meta_name, meta_value, meta_type='str') -> bool:
        """Set a models entity value if it currently exists or not."""
        if meta_name not in self.metas:
            self.metas[meta_name] = EntityMeta(self.conn, self.cursor)
            self.metas[meta_name].name = meta_name
            self.metas[meta_name].type = meta_type
        self.metas[meta_name].value = meta_value
        return True

    def meta_delete(self, meta_name) -> bool:
        """Set a models entity value if it currently exists or not."""
        sql = """
            DELETE
            FROM `%s`
            WHERE
                `entity_type` = "%s" AND
                `entity_id` = %s AND
                `name` = "%s"; """ % (
            self.table_name_meta,
            self.table_name,
            self.id,
            meta_name)
        self.cursor.execute(sql)
        return True

    def load_meta(self, model_id) -> bool:
        """Load the model's meta data."""
        sql = """
            SELECT *
            FROM %s
            WHERE
                entity_id = %s AND
                entity_type = '%s';
            """ % (self.table_name_meta, model_id, self.table_name)
        self.cursor.execute(sql)
        meta_raws = self.cursor.fetchall()
        self._load_from_meta_raw(meta_raws)
        return True

    def _load_from_meta_raw(self, meta_raws) -> bool:
        """Create self.metas for an object from raw_metas data."""
        ret_metas = {}
        for meta_raw in meta_raws:
            em = EntityMeta(self.conn, self.cursor)
            em.build_from_list(meta_raw)
            ret_metas[em.name] = em
        self.metas = ret_metas
        return True


# End File: lan-nanny/lan_nanny/modules/models/base_entitiy_meta.py
