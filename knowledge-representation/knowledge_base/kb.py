from knowledge_base.input.parser import Token
from common.frame import Frame
from common.frame import FrameSpecifier


class KnowledgeBase:
    def __init__(self):
        self.class_frames: {str: Frame} = {}
        self.instance_frames: {str: Frame} = {}
        # self.cache = []

    # v0.1
    def add_frame(self, frame: Frame) -> bool:
        if self.has_frame(frame.specs):
            return False

        if frame.specs.frame_type == FrameSpecifier.INSTANCE:
            self.instance_frames[frame.specs.frame_name] = frame
        elif frame.specs.frame_type == FrameSpecifier.CLASS:
            self.class_frames[frame.specs.frame_name] = frame

        self.update_relations(frame)

    # v0.1
    def delete_frame(self, frame_spec: FrameSpecifier):
        if frame_spec.frame_type == Token.INSTANCE:
            self.instance_frames.pop(frame_spec.frame_name)
        elif frame_spec.frame_type == Token.CLASS:
            self.class_frames.pop(frame_spec.frame_name)

    def update_frame(self, frame_spec: FrameSpecifier, add_superclasses: set = None, remove_superclasses: set = None,
                     add_subclasses: set = None, remove_subclasses: set = None,
                     add_properties: dict = None, remove_properties: set = None,
                     add_relations: dict = None, remove_relations: {str: []} = None) -> bool:
        if self.has_frame(frame_spec):
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

            frame = self.instance_frames[frame_spec.frame_name] \
                if frame_spec.frame_type == Token.INSTANCE \
                else self.class_frames[frame_spec.frame_name]

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

        self.update_relations(frame)
        return False

    # v0.1
    def view_frame(self, frame_name: str = None, frame_spec: FrameSpecifier = None):
        if frame_spec is not None:
            if frame_spec.frame_type == FrameSpecifier.CLASS and frame_spec.frame_name in self.class_frames:
                return self.class_frames[frame_spec.frame_name]
            elif frame_spec.frame_type == FrameSpecifier.INSTANCE and frame_spec.frame_name in self.instance_frames:
                return self.instance_frames[frame_spec.frame_name]
        elif frame_name is not None:
            if frame_spec.frame_name in self.class_frames:
                return self.class_frames[frame_spec.frame_name]
            elif frame_spec.frame_name in self.instance_frames:
                return self.instance_frames[frame_spec.frame_name]

        return None

    # v0.1
    def has_frame(self, frame_spec: FrameSpecifier):
        if frame_spec.frame_type == FrameSpecifier.CLASS:
            return frame_spec.frame_name in self.class_frames
        elif frame_spec.frame_type == FrameSpecifier.INSTANCE:
            return frame_spec.frame_name in self.instance_frames
        return False

    # Maintain Integrity
    def update_relations(self, frame: Frame) -> bool:
        updates = False

        for superclass in frame.superclasses:
            if superclass not in self.class_frames:
                self.add_frame(Frame(FrameSpecifier(FrameSpecifier.CLASS, superclass),
                                     subclasses={frame.specs.frame_name}))
                updates = True
            else:
                if frame.specs.frame_name not in self.class_frames[superclass].subclasses:
                    self.class_frames[superclass].subclasses.add(frame.specs.frame_name)
                    updates = True

        for subclass in frame.subclasses:
            if subclass

        return updates
