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

    def update_type(self, frame_name: str, new_type):
        if frame_name in self.class_frames or frame_name in self.instance_frames:
            frame = self.class_frames[frame_name] if frame_name in self.class_frames else self.instance_frames[frame_name]
            self.delete_frame(frame_name)
            frame.type = new_type
            self.add_frame(frame)



    def update_frame(self, frame_name, frame_type, add_superclasses: set = None, remove_superclasses: set = None,
                     add_subclasses: set = None, remove_subclasses: set = None,
                     add_properties: dict = None, remove_properties: set = None,
                     add_relations: dict = None, remove_relations: {str: []} = None) -> bool:
        if self.has_frame(frame_name):
            if add_superclasses is None:
                add_superclasses = set()
            if remove_superclasses is None:
                remove_superclasses = set()
            if add_subclasses is None:
                add_subclasses = set()
            if remove_subclasses is None:
                remove_subclasses = set()
            if add_properties is None:
                add_properties = {}
            if remove_properties is None:
                remove_properties = {}
            if add_relations is None:
                add_relations = {}
            if remove_relations is None:
                remove_relations = {}

            frame = self.instance_frames[frame_name] \
                if frame_type == Token.INSTANCE \
                else self.class_frames[frame_name]

            frame.superclasses.difference_update(remove_superclasses)
            frame.superclasses |= add_superclasses

            frame.subclasses.difference_update(remove_subclasses)
            frame.subclasses |= add_subclasses

            frame.properties |= add_properties
            for prop in remove_properties:
                del frame.properties[prop]

            frame.relations |= add_relations
            for relation, objects in remove_relations:
                for obj in objects:
                    frame.properties[relation].remove(obj)
                if len(frame.properties[relation]) == 0:
                    del frame.properties[relation]

        return False

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
