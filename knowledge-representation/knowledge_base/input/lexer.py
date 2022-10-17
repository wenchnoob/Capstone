import string


class LexerError(RuntimeError):
    pass


class Token:
    TELL = 'TELL'
    ASK = 'ASK'
    ADD = 'ADD'
    CLASS = 'CLASS'
    INSTANCE = 'INSTANCE'
    DELETE = 'DELETE'
    UPDATE = 'UPDATE'
    TYPE = 'TYPE'
    OP_PAREN = 'OP_PAREN'
    CL_PAREN = 'CL_PAREN'
    OP_SQUARE = 'OP_SQUARE'
    CL_SQUARE = 'CL_SQUARE'
    OP_CURLY = 'OP_CURLY'
    CL_CURLY = 'CL_CURLY'
    COMMA = 'COMMA'
    COLON = 'COLON'
    STR = 'STR'

    ## Maybe
    SEMICOLON = "SEMICOLON"
    DOT = "DOT"
    FILE = "FILE"
    END_FILE = "ENDFILE"
    FORWARD_SLASH = "FORWARD_SLASH"


    TYPES = {
        TELL: TELL,
        ASK: ASK,
        ADD: ADD,
        CLASS: CLASS,
        INSTANCE: INSTANCE,
        DELETE: DELETE,
        UPDATE: UPDATE,
        TYPE: TYPE,
        "(": OP_PAREN,
        ")": CL_PAREN,
        "[": OP_SQUARE,
        "]": CL_SQUARE,
        "{": OP_CURLY,
        "}": CL_CURLY,
        ",": COMMA,
        ":": COLON,
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
    def __init__(self, text: str = ""):
        self.text = text
        self.end = len(self.text)
        self.start = 0
        self.idx = 0

    def has_next_token(self):
        return self.end > self.idx

    def next_token(self):
        if not self.has_next_token():
            return None

        self.idx = self.start
        cur = self.text[self.idx]
        match cur:
            case '(' | ')' | '[' | ']' | '{' | '}' | ',' | ':':
                self.idx += 1
                self.start = self.idx
                return Token(Token.type(cur), cur)
            case '"':
                return self.qstring()
            case _:
                # if whitespace skip
                if cur in string.whitespace:
                    self.idx += 1
                    self.start = self.idx
                    return self.next_token()
                else:
                    return self.string()

    def qstring(self):
        self.idx += 1
        s = self.string()
        s.token_type = Token.STR
        self.idx += 1
        return s
    def string(self):
        cur = self.text[self.idx] if self.has_next_token() else ''

        if cur in string.ascii_letters or cur in string.digits:
            while cur in string.ascii_letters or cur in string.digits and self.has_next_token():
                self.idx += 1
                cur = self.text[self.idx] if self.has_next_token() else ''

            tok = self.text[self.start:self.idx].upper()
            self.start = self.idx
            return Token(Token.type(tok), tok)

        raise LexerError(f"Unexpected token: {cur}")

# TELL ADD CLASS Human {Animal, Mammal} [AGE:{number(x)}]

def main():
    lexer = Tokenizer(input(">"))
    while lexer.has_next_token():
        print(lexer.next_token())

main()