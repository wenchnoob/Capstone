import copy

from knowledge_base.input.parser import Token
from common.frame import Frame


class KnowledgeBase:
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

    # v0.1
    def delete_frame(self, frame_name: str):
        if frame_name in self.instance_frames:
            del self.instance_frames[frame_name]

        if frame_name in self.class_frames:
            del self.class_frames[frame_name]

    def update_type(self, frame_name: str, new_type: str):
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

    def remove_slot(self, frame_name, slot_name):
        if frame_name in self.instance_frames:
            frame = self.instance_frames[frame_name]
            frame.remove_slot(slot_name)
        elif frame_name in self.class_frames:
            frame = self.class_frames[frame_name]
            frame.remove_slot(slot_name)

    # add facet stuff if given a chance

    # v0.1
    def view_frame(self, frame_name: str = None):
        if frame_name in self.instance_frames:
            return self.instance_frames[frame_name]
        if frame_name in self.class_frames:
            return self.class_frames[frame_name]

        return None

    # v0.1
    def has_frame(self, frame_name: str):
        return frame_name in self.class_frames or frame_name in self.instance_frames

    def get_frame(self, frame_name: str):
        if frame_name in self.class_frames:
            return copy.copy(self.class_frames[frame_name])
        elif frame_name in self.instance_frames:
            return copy.copy(self.instance_frames[frame_name])
        return None

    def __str__(self):
        return "\n".join([str(x) for x in self.class_frames.values()]) + "\n" + "\n".join(
            [str(x) for x in self.instance_frames.values()])
