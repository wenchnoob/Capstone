from knowledge_base.kb import KnowledgeBase
from knowledge_base.input.parser import Parser, Node
from knowledge_base.frame import Frame, Slot


class InterpreterError(RuntimeError):
    pass


def interpret(kb: KnowledgeBase, text: str) -> None:
    root = Parser(text).parse()

    for child in root.children:
        if child.type == Node.TELL:
            interpret_tell(kb, child.children[0])
        elif child.type == Node.ASK:
            interpret_ask(kb, child)
        else:
            raise InterpreterError(f"Illegal node {child}")


def interpret_tell(kb: KnowledgeBase, node: Node) -> None:
    match node.type:
        case Node.ADD_FRAME:
            add_frame(kb, node)
        case Node.DELETE_FRAME:
            delete_frame(kb, node)
        case Node.UPDATE_FRAME:
            update_frame(kb, node)
        case _:
            raise InterpreterError(f"Illegal tell operation {node}")


def add_frame(kb, node) -> None:
    children = node.children

    frame_type = children[0].value
    frame_name = children[1].value
    superclasses = set()
    slots = {}

    if len(children) >= 3:
        ls = node.children[2].children
        if len(ls) >= 1:
            elem = ls[0]

            if elem.type == Node.LITERAL:
                for elem in ls:
                    superclasses.add(elem.value)
            elif elem.type == Node.SLOT:
                add_slots(ls, slots)

    if len(children) >= 4:
        ls = node.children[3].children
        add_slots(ls, slots)

    kb.add_frame(Frame(frame_type, frame_name, superclasses, slots))


def add_slots(children, slots) -> None:
    for slot in children:
        name = slot.children[0].value
        value = None
        facets = None
        if len(slot.children) >= 2:
            c = slot.children[1]

            if c.type == Node.LITERAL:
                value = c.value
            elif c.type == Node.FACET_LIST:
                facets = [x.value for x in c.children]

        if len(slot.children) >= 3:
            c = slot.children[2]
            facets = [x.value for x in c.children]

        slots[name] = Slot(value, facets)


def delete_frame(kb, node) -> None:
    kb.delete_frame(node.value)


def update_frame(kb, node) -> None:
    child = node.children[0]
    match child.type:
        case Node.UPDATE_TYPE:
            update_type(kb, child)
        case Node.UPDATE_NAME:
            update_name(kb, child)
        case Node.ADD_SUPER:
            add_super(kb, child)
        case Node.DELETE_SUPER:
            delete_super(kb, child)
        case Node.ADD_SLOT:
            add_slot(kb, child)
        case Node.DELETE_SLOT:
            delete_slot(kb, child)
        case Node.ADD_VALUE:
            add_value(kb, child)
        case Node.DELETE_VALUE:
            delete_value(kb, child)
        case Node.ADD_FACET:
            add_facet(kb, child)
        case Node.DELETE_FACET:
            delete_facet(kb, child)
        case Node.UPDATE_SLOT_VALUE:
            update_value(kb, child)
        case _:
            raise InterpreterError(f"Illegal node {child}")


def add_super(kb, node):
    children = node.children
    target, superclass = [n.value for n in children]
    kb.add_superclass(target, superclass)


def delete_super(kb, node):
    children = node.children
    target, superclass = [n.value for n in children]
    kb.remove_superclass(target, superclass)


def update_type(kb, node):
    children = node.children
    target, new_type = [n.value for n in children]
    kb.update_type(target, new_type)


def update_name(kb, node):
    children = node.children
    target, new_name = [n.value for n in children]
    kb.update_name(target, new_name)


def add_slot(kb, node):
    children = node.children
    name, slot = children
    slot = slot.children
    frame_name = name.value
    slot_name = slot[0].value
    slot_value = slot[1].value if len(slot) >= 2 and slot[1].type == Node.LITERAL else None
    kb.add_slot(frame_name, slot_name, slot_value)


def delete_slot(kb, node):
    target, slot = [n.value for n in node.children]
    kb.delete_slot(target, slot)


def add_value(kb, node):
    frame_name, slot_name, value = [x.value for x in node.children]
    kb.add_value(frame_name, slot_name, value)


def delete_value(kb, node):
    frame_name, slot_name, value = [x.value for x in node.children]
    kb.delete_value(frame_name, slot_name, value)


def add_facet(kb, node):
    frame_name, slot_name, facet = [x.value for x in node.children]
    kb.add_facet(frame_name, slot_name, facet)


def delete_facet(kb, node):
    frame_name, slot_name, facet = [x.value for x in node.children]
    kb.delete_facet(frame_name, slot_name, facet)


def update_value(kb, node):
    frame_name, slot_name, value = [x.value for x in node.children]
    kb.update_value(frame_name, slot_name, value)


def interpret_ask(kb: KnowledgeBase, node: Node) -> None:
    child = node.children[0]
    match child.type:
        case Node.KB:
            print(kb)
        case Node.ASK_FRAME:
            frame_name = child.children[0].value
            print(kb.get_frame(frame_name))
        case Node.TYPE:
            frame_name = child.children[0].value
            frame = kb.get_frame(frame_name)
            if frame is not None:
                print(frame.type)
            else:
                print(None)
        case Node.SLOTS:
            frame_name = child.children[0].value
            frame = kb.get_frame(frame_name)
            if frame is not None:
                print(frame.slots)
            else:
                print(None)
        case Node.SUPERS:
            frame_name = child.children[0].value
            frame = kb.get_frame(frame_name)
            if frame is not None:
                print(frame.superclasses)
            else:
                print(None)
        case Node.SUBS:
            frame_name = child.children[0].value
            frame = kb.get_frame(frame_name)
            if frame is not None:
                print(frame.subclasses)
            else:
                print(None)
        case Node.SLOT:
            frame_name = child.children[0].value
            slot_name = child.children[1].value
            frame = kb.get_frame(frame_name)
            if frame is not None:
                slots = frame.slots
                print(slots[slot_name] if slot_name in slots else 'Not a slot')
            else:
                print(None)
        case Node.TYPEOF:
            frame_name = child.children[0].value
            super_name = child.children[1].value
            frame = kb.get_frame(frame_name)
            if frame is not None:
                print(super_name in frame.superclasses)
            else:
                print(None)
        case Node.SUBBEDBY:
            frame_name = child.children[0].value
            sub_name = child.children[1].value
            frame = kb.get_frame(frame_name)
            if frame is not None:
                print(sub_name in frame.subclasses)
            else:
                print(None)
