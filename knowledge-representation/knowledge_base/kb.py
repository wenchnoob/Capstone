import copy
from knowledge_base.frame import Frame, Slot


class KnowledgeBase:
    ADD_FRAME = 'ADD_FRAME'
    UPDATE_VALUE = 'UPDATE_VALUE'
    DELETE_FRAME = 'DELETE_FRAME'

    def __init__(self):
        self.class_frames: {str: Frame} = {}
        self.instance_frames: {str: Frame} = {}
        # self.cache = []

    # v0.1
    def add_frame(self, frame: Frame) -> bool:
        if self.has_frame(frame.name):
            return False

        if frame.type == Frame.INSTANCE:
            self.instance_frames[frame.name] = frame
        elif frame.type == Frame.CLASS:
            self.class_frames[frame.name] = frame
        self.validate(frame, operation=self.ADD_FRAME)

    # v0.1
    def delete_frame(self, frame_name: str):
        if frame_name in self.instance_frames:
            del self.instance_frames[frame_name]

        if frame_name in self.class_frames:
            del self.class_frames[frame_name]
        # TODO: validate delete

    def update_type(self, frame_name: str, new_type: str):
        frame = None
        if frame_name in self.class_frames and new_type == Frame.INSTANCE:
            # Remove all subclass relations -- Instance frames dont have subclasses
            pass

        if frame_name in self.class_frames or frame_name in self.instance_frames:
            frame = self.class_frames[frame_name] if frame_name in self.class_frames else self.instance_frames[
                frame_name]
            self.delete_frame(frame_name)
            frame.type = new_type
            self.add_frame(frame)

    def update_name(self, frame_name: str, new_name: str):
        frame = None
        if frame_name in self.class_frames:
            frame = self.class_frames[frame_name]
            frame.name = new_name
            self.delete_frame(frame_name)
            self.add_frame(frame)

        # update super-sub relations to use new name

    def add_superclass(self, frame_name, super_name):
        if frame_name in self.instance_frames:
            frame = self.instance_frames[frame_name]
            if frame.add_superclass(super_name):
                self.add_subclass(super_name, frame_name)
        elif frame_name in self.class_frames:
            frame = self.class_frames[frame_name]
            if frame.add_superclass(super_name):
                self.add_subclass(super_name, frame_name)

    def remove_superclass(self, frame_name, super_name):
        frame = self.instance_frames[frame_name] if frame_name in self.instance_frames \
            else self.class_frames[frame_name] if frame_name in self.class_frames else None

        if frame is None:
            return

        if frame.remove_superclass(super_name):
            self.remove_subclass(super_name, frame_name)

    def add_subclass(self, frame_name, sub_name):
        if frame_name in self.instance_frames:
            return
        elif frame_name in self.class_frames:
            frame = self.class_frames[frame_name]
            if frame.add_subclass(sub_name):
                self.add_superclass(sub_name, frame_name)

    def remove_subclass(self, frame_name, sub_name):
        frame = self.instance_frames[frame_name] if frame_name in self.instance_frames \
            else self.class_frames[frame_name] if frame_name in self.class_frames else None

        if frame is None:
            return

        if frame.remove_subclass(sub_name):
            self.remove_superclass(sub_name, frame_name)

    def add_slot(self, frame_name, slot_name, slot_value=None):
        if frame_name in self.instance_frames:
            frame = self.instance_frames[frame_name]
            if slot_name in frame.slots:
                return
            frame.update_slot(slot_name, slot_value)
        elif frame_name in self.class_frames:
            frame = self.class_frames[frame_name]
            if slot_name in frame.slots:
                return
            frame.update_slot(slot_name, slot_value)

    def update_slot(self, frame_name, slot_name, slot_value=None):
        if frame_name in self.instance_frames:
            frame = self.instance_frames[frame_name]
            frame.update_slot(slot_name, slot_value)
        elif frame_name in self.class_frames:
            frame = self.class_frames[frame_name]
            frame.update_slot(slot_name, slot_value)

    def delete_slot(self, frame_name, slot_name):
        frame = None
        if frame_name in self.instance_frames:
            frame = self.instance_frames[frame_name]
            frame.remove_slot(slot_name)
        elif frame_name in self.class_frames:
            frame = self.class_frames[frame_name]
            frame.remove_slot(slot_name)

    def add_value(self, frame_name, slot_name, val):
        frame: Frame = self.get_frame(frame_name)
        if frame is not None:
            frame.add_value(slot_name, val)

    def delete_value(self, frame_name, slot_name, val):
        frame: Frame = self.get_frame(frame_name)
        if frame is not None:
            frame.delete_value(slot_name, val)

    def add_facet(self, frame_name, slot_name, facet):
        frame: Frame = self.get_frame(frame_name)
        if frame is not None:
            frame.add_facet(slot_name, facet)

    def delete_facet(self, frame_name, slot_name, facet):
        frame: Frame = self.get_frame(frame_name)
        if frame is not None:
            frame.delete_facet(slot_name, facet)

    def update_value(self, frame_name, slot_name, value):
        frame: Frame = self.get_frame(frame_name)
        if frame is not None:
            frame.update_slot(slot_name, value)
        self.validate(frame, operation=self.UPDATE_VALUE, slot_name=slot_name)

    # v0.1
    def has_frame(self, frame_name: str):
        return frame_name in self.class_frames or frame_name in self.instance_frames

    def get_frame(self, frame_name: str):
        if frame_name in self.class_frames:
            return self.class_frames[frame_name]
        elif frame_name in self.instance_frames:
            return self.instance_frames[frame_name]
        return None

    def __str__(self):
        return "\n".join([str(x) for x in self.class_frames.values()]) + "\n" + "\n".join(
            [str(x) for x in self.instance_frames.values()])

    def validate(self, frame: Frame, **kwargs):
        operation = kwargs.get('operation', None)
        if frame is None and operation != KnowledgeBase.DELETE_FRAME:
            return

        match operation:
            case KnowledgeBase.ADD_FRAME:
                new_supers = set()
                for clazz in frame.superclasses:
                    self.add_subclass(clazz, frame.name)
                    superclass: Frame = self.get_frame(clazz)
                    if superclass is not None:
                        new_supers.update(superclass.superclasses)
                        for key in superclass.slots:
                            frame.update_slot(key, superclass.slots.get(key))
                frame.superclasses.update(new_supers)

                if frame.typeof('FOOD') and frame.is_instance():
                    frame.update_slot('START_DAY', self.get_frame('MY_CALENDAR').slots['CURRENT_DAY'].values[0])
            case KnowledgeBase.UPDATE_VALUE:
                slot_name = kwargs.get('slot_name')

                if frame.typeof('CALENDAR') and slot_name == 'CURRENT_DAY':
                    self.update_foods()
            case _:
                pass

    def update_foods(self):
        frame = self.get_frame('FOOD')
        if frame is None:
            return
        for subclass in frame.subclasses:
            self.update_food(subclass)

    def update_food(self, food):
        frame = self.get_frame(food)
        if frame is None:
            return
        elif frame.is_instance():
            lifespan = int(frame.slots['LIFESPAN'].values[0])
            if lifespan != 0:
                frame.slots['LIFESPAN'].values[0] = lifespan - 1

            if int(frame.slots['LIFESPAN'].values[0]) == 0:
                frame.slots['SPOILAGE_DAY'].values[0] = self.get_frame('MY_CALENDAR').slots['CURRENT_DAY'].values[0]
                frame.slots['SPOILED'].values[0] = 'YES'
        else:
            for subclass in frame.subclasses:
                self.update_food(subclass)



