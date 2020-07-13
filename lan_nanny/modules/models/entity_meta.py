"""Entity Meta Model

How to use:
    The Device model is a good example to follow.

    To give a model the ability to use EntityMetas the class must:
        - extend the BaseEntityMeta
        - define a `self.metas = {}` in the init

    To set a new EntityMeta value for an object which may or may not have the EntityMeta yet.

        if 'notes' not in device.metas:
            # Create the notes meta if it doesn't exist
            device.metas['notes'] = EntityMetas()
            device.metas['notes'].create(
                meta_name='notes',
                meta_type='str',
                meta_value=device_notes)
        else:
            # Update the device notes.
            device.metas['notes'].value = request.form['device_notes']

"""
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
        """Build a model from an ordered list, converting data types to their desired type where
           possible.
        """
        count = 0
        for field in self.total_map:
            setattr(self, field['name'], raw[count])
            count += 1
            if self.type == 'bool':
                self.value = self._set_bool(self.value)

        return True

    def create(self, meta_name: str, meta_type: str, meta_value: str=None) -> bool:
        """Initiate a new EntityMeta object with a name, type and optional value. 

        :param meta_name: The meta key name for the entity meta.
        :param meta_type: The meta's data type. Supported str, int and bool currently.
        :param meta_value: The value to set for the meta.
        """
        self.name = meta_name
        self.type = meta_type
        self.value = meta_value
        self.entity_type = self.table_name

        # Validate the data type for the entity meta
        if self.type not in ['str', 'int', 'bool']:
            raise AttributeError('Invalid EntityMeta type: %s' % self.type)

        # Validate the entity_type, which requires the model to set the `self.table_name` var.
        if not self.entity_type:
            raise AttributeError("Invalid EntityType type: %s, must set model's self.table_name" % self.entity_type)

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
