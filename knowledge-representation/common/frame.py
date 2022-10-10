class FrameSpecifier:
    INSTANCE = 'INSTANCE'
    CLASS = 'CLASS'
    UNKNOWN = 'UNKNOWN'

    def __init__(self, frame_type: str, frame_name: str):
        self.frame_type = frame_type
        self.frame_name = frame_name


class Frame:
    def __init__(self, specs: FrameSpecifier, superclasses: set = None, subclasses: set = None, properties: dict = None,
                 relations: dict = None):

        if superclasses is None:
            superclasses = set()
        if subclasses is None:
            subclasses = set()
        if properties is None:
            properties = {}
        if relations is None:
            relations = {}

        self.specs = specs
        self.superclasses = superclasses
        self.subclasses = subclasses
        self.properties = properties
        self.relations = relations

    def add_superclass(self, superclass: str) -> bool:
        self.superclasses.add(superclass)
        return True

    def remove_superclass(self, superclass: str) -> bool:
        self.superclasses.remove(superclass)
        return True

    def add_subclass(self, subclass: str) -> bool:
        if self.specs.frame_type == FrameSpecifier.INSTANCE:
            return False
        else:
            self.superclasses.add(subclass)
            return True

    def remove_subclass(self, subclass: str) -> bool:
        self.superclasses.remove(subclass)
        return True

    def update_property(self, key: str, val) -> bool:
        self.properties[key] = val
        return True

    def remove_property(self, key: str):
        if key in self.properties:
            del self.properties[key]

    def update_properties(self, keys_vals: []) -> bool:
        for t in keys_vals:
            key, val = t
            self.update_property(key, val)
        return True

    def add_relation(self, relation, clazz):
        if relation in self.relations:
            self.relations[relation].append(clazz)
        else:
            self.relations[relation] = [clazz]

    def remove_relation(self, relation, clazz):
        if relation in self.relations:
            self.relations[relation].remove(clazz)

    def __repr__(self):
        return f'{self.specs.frame_type} FRAME (name={self.specs.frame_name}, superclasses={{{", ".join(self.superclasses)}}}, ' \
               f'subclasses={{{", ".join(self.subclasses)}}}, properties={self.properties}, relations={self.relations}) '
