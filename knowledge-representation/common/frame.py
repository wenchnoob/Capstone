class Frame:
    # ADD FACETS and Facet logic if given the time
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
        self.superclasses.add(subclass)
        return True

    def remove_subclass(self, subclass: str) -> bool:
        if self.is_instance() or subclass not in self.subclasses:
            return False
        self.superclasses.remove(subclass)
        return True

    def update_slot(self, key: str, val) -> bool:
        self.slots[key] = val
        return True

    def update_slots(self, keys_vals: []) -> bool:
        for t in keys_vals:
            key, val = t
            self.update_slot(key, val)
        return True

    def remove_slot(self, key: str):
        if key in self.slots:
            del self.slots[key]

    def is_instance(self) -> bool:
        return self.type == Frame.INSTANCE

    def __repr__(self):
        return f'{self.type} FRAME (name={self.name}, superclasses={{{", ".join(self.superclasses)}}}, ' \
               f'subclasses={{{", ".join(self.subclasses)}}}, slots={self.slots}) '
