from knowledge_base.kb import KnowledgeBase
from knowledge_base.input.interpreter import interpret


def main():
    kb = KnowledgeBase()
    line = input("> ").upper()

    while line != 'EXIT':
        interpret(kb, line)
        line = input("> ").upper()


if __name__ == "__main__":
    main()

# update instance frame wenchy add superclasses [engineer]
# view instance frame wenchy
# add instance frame (wenchy, [], [], {}, {})
# view instance frame wenchy
# update instance frame wenchy add superclasses [engineer]
#
