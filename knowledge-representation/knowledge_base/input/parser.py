from knowledge_base.input.lexer import Tokenizer, Token


class ParseError(RuntimeError):
    pass


class Node:
    TELL = 'TELL'

    ADD_FRAME = 'ADD_FRAME'
    CLASS = 'CLASS'
    INSTANCE = 'INSTANCE'
    DELETE_FRAME = 'DELETE_FRAME'

    UPDATE_FRAME = 'UPDATE_FRAME'
    UPDATE_TYPE = 'UPDATE_TYPE'
    UPDATE_NAME = 'UPDATE_NAME'
    ADD_SUPER = 'ADD_SUPER'
    DELETE_SUPER = 'DELETE_SUPER'
    ADD_SLOT = 'ADD_SLOT'
    DELETE_SLOT = 'DELETE_SLOT'

    UPDATE_SLOT = 'UPDATE_SLOT'
    FACET = 'FACET'
    ADD_FACET = 'ADD_FACET'
    DELETE_FACET = 'DELETE_FACET'

    ASK = 'ASK'
    TYPE = 'TYPE'

    LITERAL = 'LITERAL'
    LIST = 'LIST'
    SLOT = 'SLOT'

    # Maybe
    UPDATE_FACET = 'UPDATE_FACET'

    def __init__(self, type=None, value=None, children=None):
        if children is None:
            children = []
        self.type = type
        self.value = value
        self.children = children

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return self.str(0)

    def str(self, d):
        space = "    "
        s = f"{space * d}(Type={self.type}, Value={self.value})\n"
        for c in self.children:
            s += c.str(d + 1)
        return s


class Parser:
    def __init__(self, text: str):
        self.tokenizer = Tokenizer(text)
        self.lookahead = self.tokenizer.next_token()

    def advance(self):
        self.lookahead = self.tokenizer.next_token()

    def eat(self, token_type: str) -> str:
        if self.lookahead is None:
            raise ParseError(f"unexpected end of input")
        if self.lookahead.token_type != token_type:
            self.fail()
        value = self.lookahead.value
        self.advance()
        return value

    def EOF(self):
        if self.lookahead is None:
            return True
        return False

    def fail(self):
        raise ParseError(f"unexpected token {self.lookahead}")

    def parse(self) -> Node:
        root = Node()

        while not self.EOF():
            match self.lookahead.token_type:
                case Token.TELL:
                    root.add_child(self.tell())
                case Token.ASK:
                    root.add_child(self.ask())
                case _:
                    self.fail()

        return root

    def tell(self) -> Node:
        self.advance()

        tell = Node(Node.TELL)

        match self.lookahead.token_type:
            case Token.ADD:
                tell.add_child(self.add_frame())
            case Token.UPDATE:
                tell.add_child(self.update_frame())
            case Token.DELETE:
                tell.add_child(self.delete_frame())
            case _:
                self.fail()

        return tell

    def add_frame(self) -> Node:
        self.eat(Token.ADD)

        add_class = Node(Node.ADD_FRAME)

        frame_type = self.type()
        add_class.add_child(frame_type)

        frame_name = self.literal()
        add_class.add_child(frame_name)

        if not self.EOF() and self.lookahead.token_type == Token.OP_CURLY:
            super_classes = self.list(Token.OP_CURLY, Token.CL_CURLY, self.literal)
            add_class.add_child(super_classes)

        if not self.EOF() and self.lookahead.token_type == Token.OP_SQUARE:
            slots = self.list(Token.OP_SQUARE, Token.CL_SQUARE, self.slot)
            add_class.add_child(slots)

        return add_class

    def slot(self):
        slot = Node(Node.SLOT)

        slot_name = self.literal()
        slot.add_child(slot_name)
        self.eat(Token.COLON)

        if self.lookahead.token_type != Token.CL_SQUARE and self.lookahead.token_type != Token.OP_CURLY and \
                self.lookahead.token_type != Token.COMMA:
            slot_value = self.literal()
            slot.add_child(slot_value)

        if self.lookahead.token_type != Token.CL_SQUARE and self.lookahead.token_type != Token.COMMA:
            facets = self.list(Token.OP_CURLY, Token.CL_CURLY, self.facet)
            slot.add_child(facets)

        return slot

    def facet(self) -> Node:
        facet = Node(Node.FACET)

        facet_name = self.literal()
        facet.add_child(facet_name)

        args = self.list(Token.OP_PAREN, Token.CL_PAREN, self.literal)
        facet.add_child(args)

        return facet

    def update_frame(self) -> Node:
        self.eat(Token.UPDATE)
        tk_name = self.literal()

        lookahead = self.lookahead
        children = []
        # print(lookahead.token_type)
        match lookahead.token_type:
            case Token.NAME:
                self.eat(Token.NAME)
                self.eat(Token.TO)
                children = [Node(Node.UPDATE_NAME, None, [tk_name, self.literal()])]
            case Token.TYPE:
                self.eat(Token.TYPE)
                self.eat(Token.TO)
                children = [Node(Node.UPDATE_TYPE, None, [tk_name, self.type()])]
            case Token.ADD | Token.DELETE:
                children = [tk_name, self.add_super_or_slot()]
            case Token.UPDATE:
                self.eat(Token.UPDATE)
                self.eat(Token.SLOT)
                children = [tk_name, self.literal(), self.update_slot()]
            case _:
                self.fail()
        return Node(Node.UPDATE_FRAME, None, children)

    def delete_frame(self) -> Node:
        self.eat(Token.DELETE)
        name = self.eat(Token.STR)
        return Node(Node.DELETE_FRAME, name)

    def add_super_or_slot(self):
        tok_type = self.lookahead.token_type
        if tok_type == Token.ADD:
            self.eat(Token.ADD)
            tok_type = self.lookahead.token_type
            if tok_type == Token.SUPER:
                self.eat(Token.SUPER)
                return Node(Node.ADD_SUPER, self.eat(Token.STR))
            elif tok_type == Token.SLOT:
                self.eat(Token.SLOT)
                return Node(Node.ADD_SLOT, None, [self.slot()])
            else:
                self.fail()
        elif tok_type == Token.DELETE:
            self.eat(Token.DELETE)
            tok_type = self.lookahead.token_type
            if tok_type == Token.SUPER:
                self.eat(Token.SUPER)
                return Node(Node.DELETE_SUPER, None, [self.literal()])
            elif tok_type == Token.SLOT:
                self.eat(Token.SLOT)
                return Node(Node.DELETE_SLOT, None, [self.literal()])
        elif tok_type == Token.UPDATE:
            return Node(Node.UPDATE_SLOT, None, [self.literal(), self.update_slot()])
        else:
            self.fail()

    def update_slot(self):
        tok_type = self.lookahead.token_type
        if tok_type == Token.ADD:
            self.eat(Token.ADD)
            self.eat(Token.FACET)
            return Node(Node.ADD_FACET, None, [self.facet()])
        elif tok_type == Token.DELETE:
            self.eat(Token.DELETE)
            self.eat(Token.FACET)
            return Node(Node.DELETE_FACET, self.eat(Token.STR))
        else:
            self.fail()

    def ask(self) -> Node:
        pass

    def list(self, op_tok, cl_tok, element) -> Node:
        self.eat(op_tok)
        ls = Node(Node.LIST)
        while self.lookahead.token_type != cl_tok:
            ls.add_child(element())
            if self.lookahead.token_type != cl_tok:
                self.eat(Token.COMMA)
        self.eat(cl_tok)
        return ls

    def type(self) -> Node:
        lookahead = self.lookahead.token_type
        self.advance()
        match lookahead:
            case Token.CLASS:
                return Node(Node.TYPE, Node.CLASS)
            case Token.INSTANCE:
                return Node(Node.TYPE, Node.INSTANCE)
            case _:
                self.fail()

    def literal(self) -> Node:
        return Node(Node.LITERAL, self.eat(Token.STR))

