from typing import Iterable, Union
from knowledge_base.input.lexer import Tokenizer, Token
from common.frame import Frame, FrameSpecifier


class ParseError(RuntimeError):
    pass


class KBOperation:
    ADD = "ADD"
    UPDATE_ADD = "UPDATE_ADD"
    UPDATE_DELETE = "UPDATE_DELETE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    VIEW_ALL = "VIEWALL"
    PROPERTIES = "PROPERTIES"
    RELATIONS = "RELATIONS"

    def __init__(self, op_type: str, frame: Frame = None):
        self.op_type = op_type
        self.frame = frame

    def __repr__(self):
        return f"(Operation={self.op_type}, Frame={self.frame})"


'''
Lang:

statement_list ::=
    statement; statement_list |
    ε

statement ::=
    ADD  frame |
    UPDATE [INSTANCE | CLASS] FRAME frame_name update_statement |
    (DELETE | VIEW) [INSTANCE | CLASS] FRAME frame_name
    
    
frame ::=
    [INSTANCE | CLASS] FRAME (frame_name, list, list, map, map)

list ::=
    [ list_elems ]

list_elems ::=
    ne_list_elems | ε

ne_list_elems ::=
    (STR | NUM | BOOL | list) , ne_list_elems |
    (STR | NUM | BOOL | list)

map ::=
    { pairs }

pairs ::=
    ne_pairs | ε

ne_pairs ::=
    pair, ne_pairs |
    pair

pair ::=
    STR:(STR | NUM | BOOL | list | ε)

update_statement ::=
    (ADD | DELETE) (SUPERCLASS | SUBCLASS) frame_name  |
    (ADD | DELETE) (PROPERTIES | RELATIONS) (properties | relation)

frame_name ::=
    STR
'''


class Parser:
    def __init__(self, text: str = None):
        self.tokenizer = None
        self.lookahead = None
        if text is not None:
            self.init(text)

    def init(self, text: str):
        self.tokenizer = Tokenizer(text)
        self.lookahead = self.tokenizer.next_token()

    def advance(self):
        self.lookahead = self.tokenizer.next_token()

    def fail(self):
        raise ParseError(f"unexpected token {self.lookahead}")

    def eat(self, token_type: str) -> Union[int, str, bool]:
        if self.lookahead is None:
            raise ParseError(f"unexpected end of input")
        if self.lookahead.token_type != token_type:
            self.fail()
        value = self.lookahead.value
        self.advance()
        return value

    def eat_ls(self, token_types: Iterable[str]) -> Union[int, str, bool]:
        if self.lookahead is None:
            raise ParseError(f"unexpected end of input")
        if self.lookahead.token_type not in token_types:
            self.fail()
        value = self.lookahead.value
        self.advance()
        return value

    def parse(self, text: str = None) -> [KBOperation]:
        if text is not None:
            self.init(text)

        operations = []
        while self.tokenizer.has_next_token():
            stmt = self.statement()
            if isinstance(stmt, list):
                operations.extend(stmt)
            else:
                operations.append(stmt)
            if self.lookahead is not None and self.lookahead.token_type == Token.SEMICOLON:
                self.eat(Token.SEMICOLON)

        return operations

    def statement(self):
        if self.lookahead is None:
            raise ParseError(f"unexpected end of input")
        match self.lookahead.token_type:
            case Token.ADD:
                return self.add()
            case Token.UPDATE:
                return self.update()
            case Token.DELETE | Token.VIEW:
                return self.delete_or_view()
            case Token.FILE:
                return self.file()
            case Token.VIEW_ALL:
                return KBOperation(KBOperation.VIEW_ALL)
            case _:
                raise ParseError(f"unexpected token: {self.lookahead}")

    def file(self):
        self.eat(Token.FILE)
        file_name = self.file_name()
        with open(file_name, 'r') as file:
            return Parser().parse("".join(file.readlines()))

    def file_name(self) -> str:
        file_name = ""
        while self.lookahead is not None and self.lookahead.token_type != Token.END_FILE:
            file_name += self.eat_ls([Token.STR, Token.FORWARD_SLASH, Token.DOT])
        self.eat(Token.END_FILE)
        return file_name

    def add(self):
        self.eat(Token.ADD)
        return KBOperation(KBOperation.ADD, self.frame())

    def frame(self):
        frame_type = self.eat_ls([Token.INSTANCE, Token.CLASS])
        self.eat(Token.FRAME)
        self.eat(Token.OP_PAREN)
        frame_name = self.eat(Token.STR)
        self.eat(Token.COMMA)
        superclasses = self.ls()
        self.eat(Token.COMMA)
        subclasses = self.ls()
        self.eat(Token.COMMA)
        properties = self.properties()
        self.eat(Token.COMMA)
        relations = self.relations()
        self.eat(Token.CL_PAREN)
        return Frame(FrameSpecifier(frame_type, frame_name), set(superclasses), set(subclasses), properties, relations)

    def ls(self):
        ls = []
        self.eat(Token.OP_SQUARE)
        while self.lookahead is not None and self.lookahead.token_type != Token.CL_SQUARE:
            ls.append(self.eat(Token.STR))
            if self.lookahead.token_type == Token.COMMA:
                self.eat(Token.COMMA)
        self.eat(Token.CL_SQUARE)
        return ls

    def properties(self):
        properties = {}
        self.eat(Token.OP_CURLY)
        while self.lookahead is not None and self.lookahead.token_type != Token.CL_CURLY:
            key = self.eat(Token.STR)
            self.eat(Token.COLON)
            val = self.eat(Token.STR)
            properties[key] = val
            if self.lookahead is not None and self.lookahead.token_type == Token.CL_CURLY:
                self.eat(Token.COMMA)
        self.eat(Token.CL_CURLY)
        return properties

    def relations(self):
        relations = {}
        self.eat(Token.OP_CURLY)
        while self.lookahead is not None and self.lookahead.token_type != Token.CL_CURLY:
            key = self.eat(Token.STR)
            self.eat(Token.COLON)
            val = self.ls()
            relations[key] = val
            if self.lookahead is not None and self.lookahead.token_type != Token.CL_CURLY:
                self.eat(Token.COMMA)
        self.eat(Token.CL_CURLY)
        return relations

    def delete_or_view(self):
        operation = None
        if self.lookahead is not None and self.lookahead.token_type == Token.VIEW:
            operation = KBOperation.VIEW
        elif self.lookahead is not None and self.lookahead.token_type == Token.DELETE:
            operation = KBOperation.DELETE
        else:
            self.fail()

        self.eat_ls([Token.VIEW, Token.DELETE])
        frame_type = self.eat_ls([Token.INSTANCE, Token.CLASS])
        self.eat(Token.FRAME)
        frame_name = self.eat(Token.STR)

        return KBOperation(operation, Frame(FrameSpecifier(frame_type, frame_name)))

    '''
    UPDATE [INSTANCE | CLASS] FRAME frame_name update_statement |
    
    update_statement ::=
    (ADD | DELETE) (SUPERCLASS | SUBCLASS) frame_name  |
    (ADD | DELETE) (PROPERTY | RELATION) (properties | relation)
    '''

    def update(self):
        self.eat(Token.UPDATE)
        frame_type = self.eat_ls([Token.INSTANCE, Token.CLASS])
        self.eat(Token.FRAME)
        frame_name = self.eat(Token.STR)

        operation = None
        if self.lookahead.token_type == Token.ADD:
            operation = KBOperation.UPDATE_ADD
        elif self.lookahead.token_type == Token.DELETE:
            operation = KBOperation.UPDATE_DELETE
        self.eat_ls([Token.ADD, Token.DELETE])

        target_part = self.eat_ls([Token.SUPERCLASSES, Token.SUBCLASSES, Token.PROPERTIES, Token.RELATIONS])
        if target_part == Token.SUPERCLASSES:
            return KBOperation(operation, Frame(FrameSpecifier(frame_type, frame_name), set(self.ls()), set(), {}, {}))
        elif target_part == Token.SUBCLASSES:
            return KBOperation(operation, Frame(FrameSpecifier(frame_type, frame_name), set(), set(self.ls()), {}, {}))
        elif target_part == Token.PROPERTIES:
            return KBOperation(operation, Frame(FrameSpecifier(frame_type, frame_name), set(), set(),
                                                self.properties(), {}))
        elif target_part == Token.RELATIONS:
            return KBOperation(operation, Frame(FrameSpecifier(frame_type, frame_name), set(), set(), {}, self.relations()))

