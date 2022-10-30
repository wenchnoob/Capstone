class Facets:
    NUMBER = 'NUMBER'
    MULTIVALUED = 'MULTIVALUED'
    SYMMETRIC = 'SYMMETRIC'


class Slot:
    def __init__(self, values, facets):
        if not isinstance(values, list):
            self.values = [values]
        else:
            self.values = values

        if not isinstance(facets, list):
            self.facets = [facets]
        else:
            self.facets = facets

    def __str__(self):
        if Facets.MULTIVALUED not in self.facets:
            if len(self.values) >= 1:
                return f'(value={self.values[0]}, facets={self.facets})'
        return f'(value={self.values}, facets={self.facets})'

    def __repr__(self):
        return self.__str__()


class Frame:
    INSTANCE = 'INSTANCE'
    CLASS = 'CLASS'

    def __init__(self, frame_type: str, frame_name: str, superclasses: set = None,
                 slots: dict = None):

        if superclasses is None:
            superclasses = set()
        if slots is None:
            slots = {}

        self.name = frame_name
        self.type = frame_type
        self.superclasses = superclasses
        self.subclasses = set()
        self.slots = slots

    def add_superclass(self, superclass: str) -> bool:
        if superclass in self.superclasses:
            return False
        self.superclasses.add(superclass)
        return True

    def remove_superclass(self, superclass: str) -> bool:
        if superclass not in self.superclasses:
            return False
        self.superclasses.remove(superclass)
        return True

    def add_subclass(self, subclass: str) -> bool:
        if self.is_instance() or subclass in self.subclasses:
            return False
        self.subclasses.add(subclass)
        return True

    def remove_subclass(self, subclass: str) -> bool:
        if self.is_instance() or subclass not in self.subclasses:
            return False
        self.superclasses.remove(subclass)
        return True

    def update_slot(self, key: str, val) -> bool:
        # validate update in relation to facets
        if key not in self.slots:
            self.slots[key] = val
        else:
            self.slots[key].values[0] = val
        return True

    def add_value(self, key: str, val) -> bool:
        if key in self.slots:
            slot: Slot = self.slots[key]
            slot.values.append(val)
            return True
        return False

    def delete_value(self, key: str, val) -> bool:
        if key in self.slots:
            slot: Slot = self.slots[key]
            if val in slot.values:
                del slot.values[val]
                return True
        return False

    def add_facet(self, key: str, facet: str) -> bool:
        if key in self.slots:
            slot: Slot = self.slots[key]
            slot.facets.append(facet)
            return True
        return False

    def delete_facet(self, key: str, facet: str) -> bool:
        if key in self.slots:
            slot: Slot = self.slots[key]
            if facet in slot.facets:
                del slot.facets[facet]
                return True
        return False

    def remove_slot(self, key: str):
        if key in self.slots:
            del self.slots[key]
            return True
        return False

    def is_instance(self) -> bool:
        return self.type == Frame.INSTANCE

    def typeof(self, superframe):
        if superframe in self.superclasses or self.name == superframe:
            return True
        return False

    def __repr__(self):
        return f'{self.type} FRAME (name={self.name}, superclasses={{{", ".join(self.superclasses)}}}, ' \
               f'subclasses={{{", ".join(self.subclasses)}}}, slots={self.slots}) '


