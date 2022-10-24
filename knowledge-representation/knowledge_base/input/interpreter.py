from knowledge_base.kb import KnowledgeBase
from knowledge_base.input.parser import Parser
from parser import Node
from common.frame import Frame


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
                if len(children) >= 4:
                    ls = node.children[3].children
                    add_slots(ls, slots)
            elif elem.type == Node.SLOT:
                add_slots(ls, slots)

    kb.add_frame(Frame(frame_type, frame_name, superclasses, slots))


def add_slots(children, slots):
    for slot in children:
        name = slot.children[0].value
        value = slot.children[1].value if len(slot.children) >= 2 else None
        slots[name] = value


def delete_frame(kb, node) -> bool:
    kb.delete_frame(node.value)


def update_frame(kb, node) -> None:
    print(node)

    child = node.children[0]

    match child.type:
        case Node.UPDATE_TYPE:
            update_type(kb, child)
        case Node.UPDATE_NAME:
            update_name(kb, child)
        case Node.UPDATE_SLOT:
            update_slot(kb, child)
        case Node.UPDATE_FACET:
            update_facet(kb, child)
        case _:
            raise InterpreterError(f"Illegal node {child}")


def update_type(kb, node):
    children = node.children
    target, new_type = [n.value for n in children]
    kb.update_type(target, new_type)


def update_name(kb, node):
    pass


def update_slot(kb, node):
    pass


def update_facet(kb, node):
    pass


def interpret_ask(kb: KnowledgeBase, node: Node) -> None:
    pass


# TELL ADD CLASS Human {Animal, Mammal} [Age:]

def main():
    kb = KnowledgeBase()
    x = input()
    while x != "":
        if x == "VIEW":
            frame = input("> Frame? (empty for all): ")
            if frame != "":
                print(kb.view_frame(frame))
            else:
                pass
        else:
            interpret(kb, x)
        x = input()


if __name__ == '__main__':
    main()
