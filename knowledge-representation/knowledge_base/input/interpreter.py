from knowledge_base.kb import KnowledgeBase
from knowledge_base.input.parser import Parser, KBOperation


def interpret(kb: KnowledgeBase, text: str) -> None:
    operations = Parser(text).parse()
    for operation in operations:
        frame = operation.frame

        match operation.op_type:
            case KBOperation.ADD:
                kb.add_frame(frame)
            case KBOperation.DELETE:
                kb.delete_frame(frame)
            case KBOperation.VIEW:
                print(kb.view_frame(frame_spec=frame.specs))
            case KBOperation.UPDATE_DELETE:
                kb.update_frame(operation.frame.specs, remove_superclasses=frame.superclasses,
                                remove_relations=frame.relations,
                                remove_subclasses=frame.subclasses, remove_properties=frame.properties)
            case KBOperation.UPDATE_ADD:
                kb.update_frame(operation.frame.specs, add_superclasses=frame.superclasses,
                                add_relations=frame.relations,
                                add_subclasses=frame.subclasses, add_properties=frame.properties)
            case KBOperation.VIEW_ALL:
                print("Instances")
                for k, v in kb.instance_frames.items():
                    print(f"\t{k}: {v}")
                print("Classes")
                for k, v in kb.class_frames.items():
                    print(f"\t{k}: {v}")
            case other:
                raise RuntimeError(f"Failed to interpret {other}")
