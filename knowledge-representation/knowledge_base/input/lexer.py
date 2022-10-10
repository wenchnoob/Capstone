import string
from common.frame import FrameSpecifier


class LexerError(RuntimeError):
    pass


class Token:
    ADD = 'ADD'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    VIEW = 'VIEW'
    CLASS = FrameSpecifier.CLASS
    INSTANCE = FrameSpecifier.INSTANCE
    FRAME = 'FRAME'
    VIEW_ALL = 'VIEWALL'
    SUPERCLASSES = 'SUPERCLASSES'
    SUBCLASSES = 'SUBCLASSES'
    PROPERTIES = 'PROPERTIES'
    RELATIONS = 'RELATIONS'
    OP_PAREN = 'OP_PAREN'
    CL_PAREN = 'CL_PAREN'
    OP_SQUARE = 'OP_SQUARE'
    CL_SQUARE = 'CL_SQUARE'
    OP_CURLY = 'OP_CURLY'
    CL_CURLY = 'CL_CURLY'
    COMMA = 'COMMA'
    COLON = 'COLON'
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"
    FILE = "FILE"
    END_FILE = "ENDFILE"
    FORWARD_SLASH = "FORWARD_SLASH"
    STR = 'STR'

    TYPES = {
        ADD: ADD,
        UPDATE: UPDATE,
        DELETE: DELETE,
        VIEW: VIEW,
        CLASS: CLASS,
        INSTANCE: INSTANCE,
        FRAME: FRAME,
        SUPERCLASSES: SUPERCLASSES,
        SUBCLASSES: SUBCLASSES,
        PROPERTIES: PROPERTIES,
        RELATIONS: RELATIONS,
        FILE: FILE,
        VIEW_ALL: VIEW_ALL,
        END_FILE: END_FILE,
        "(": OP_PAREN,
        ")": CL_PAREN,
        "[": OP_SQUARE,
        "]": CL_SQUARE,
        "{": OP_CURLY,
        "}": CL_CURLY,
        ",": COMMA,
        ":": COLON,
        ";": SEMICOLON,
        "/": FORWARD_SLASH,
        ".": DOT
    }

    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        return f"Token(type={self.token_type}, value={self.value})"

    @staticmethod
    def type(value):
        if value in Token.TYPES:
            return Token.TYPES[value]
        else:
            return Token.STR


class Tokenizer:
    def __init__(self, text=""):
        self.text = text
        self.idx = 0
        self.start = 0

    def init(self, text: str):
        self.text = text
        self.idx = 0
        self.start = 0

    def has_next_token(self):
        return len(self.text) > self.idx

    def next_token(self):
        if not self.has_next_token():
            return None

        self.idx = self.start
        cur = self.text[self.idx]
        match cur:
            case '(' | ')' | '[' | ']' | '{' | '}' | ',' | ':' | ';' | '/' | '.':
                self.idx += 1
                self.start = self.idx
                return Token(Token.type(cur), cur)
            case '"':
                self.idx += 1
                try:
                    cur = self.text[self.idx]
                except IndexError:
                    raise LexerError("Unexpected end of input while parsing string")
                while cur != '"':
                    self.idx += 1
                    try:
                        cur = self.text[self.idx]
                    except IndexError:
                        raise LexerError("Unexpected end of input while parsing string")

                tok = self.text[self.start+1:self.idx].upper()
                self.start = self.idx+1
                return Token(Token.type(tok), tok)
            case other:
                if other in string.whitespace:
                    self.idx += 1
                    self.start = self.idx
                    return self.next_token()

                if cur in string.ascii_letters or cur in string.digits:
                    while cur in string.ascii_letters or cur in string.digits and self.has_next_token():
                        self.idx += 1
                        cur = self.text[self.idx] if self.has_next_token() else '.'

                    tok = self.text[self.start:self.idx ].upper()
                    self.start = self.idx
                    return Token(Token.type(tok), tok)

                raise LexerError(f"Unexpected token: {cur}")


#tokenizer = Tokenizer('ADD INSTANCE FRAME (Wenchy, [], [], {}, {"is a":[engineer, artist, male]})"')

