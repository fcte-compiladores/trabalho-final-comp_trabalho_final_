"""
Análise léxica para a linguagem Lox.
"""

from typing import List, Optional, Any
from .token_types import Token, TokenType, KEYWORDS
from .lox_error import LoxError


class Lexer:
    """Analisador léxico para a linguagem Lox."""

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> List[Token]:
        """Escaneia o código fonte e retorna uma lista de tokens."""
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def _scan_token(self):
        """Escaneia um único token."""
        c = self._advance()

        # Tokens de um caractere
        if c == '(':
            self._add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self._add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self._add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self._add_token(TokenType.RIGHT_BRACE)
        elif c == '[':
            self._add_token(TokenType.LEFT_BRACKET)
        elif c == ']':
            self._add_token(TokenType.RIGHT_BRACKET)
        elif c == ',':
            self._add_token(TokenType.COMMA)
        elif c == '.':
            self._add_token(TokenType.DOT)
        elif c == '-':
            if self._match('='):
                self._add_token(TokenType.MINUS_EQUAL)
            else:
                self._add_token(TokenType.MINUS)
        elif c == '+':
            if self._match('='):
                self._add_token(TokenType.PLUS_EQUAL)
            else:
                self._add_token(TokenType.PLUS)
        elif c == ';':
            self._add_token(TokenType.SEMICOLON)
        elif c == '*':
            self._add_token(TokenType.STAR)
        elif c == '%':
            self._add_token(TokenType.PERCENT)
        # Tokens de um ou dois caracteres
        elif c == '!':
            self._add_token(TokenType.BANG_EQUAL if self._match('=') else TokenType.BANG)
        elif c == '=':
            self._add_token(TokenType.EQUAL_EQUAL if self._match('=') else TokenType.EQUAL)
        elif c == '<':
            self._add_token(TokenType.LESS_EQUAL if self._match('=') else TokenType.LESS)
        elif c == '>':
            self._add_token(TokenType.GREATER_EQUAL if self._match('=') else TokenType.GREATER)
        elif c == '/':
            if self._match('/'):
                # Comentário até o final da linha
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            elif self._match('*'):
                # Comentário de bloco
                self._block_comment()
            else:
                self._add_token(TokenType.SLASH)
        # Ignorar espaços em branco
        elif c in [' ', '\r', '\t']:
            pass
        elif c == '\n':
            self.line += 1
        # Strings
        elif c == '"':
            self._string()
        else:
            if c.isdigit():
                self._number()
            elif c.isalpha() or c == '_':
                self._identifier()
            else:
                raise LoxError(self.line, f"Caractere inesperado: {c}")

    def _block_comment(self):
        """Processa comentários de bloco /* ... */."""
        depth = 1
        while depth > 0 and not self._is_at_end():
            if self._peek() == '/' and self._peek_next() == '*':
                depth += 1
                self._advance()
                self._advance()
            elif self._peek() == '*' and self._peek_next() == '/':
                depth -= 1
                self._advance()
                self._advance()
            else:
                if self._peek() == '\n':
                    self.line += 1
                self._advance()

    def _identifier(self):
        """Processa identificadores e palavras-chave."""
        while self._peek().isalnum() or self._peek() == '_':
            self._advance()

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        self._add_token(token_type)

    def _number(self):
        """Processa números."""
        while self._peek().isdigit():
            self._advance()

        # Procura por parte fracionária
        if self._peek() == '.' and self._peek_next().isdigit():
            # Consome o '.'
            self._advance()

            while self._peek().isdigit():
                self._advance()

        value = float(self.source[self.start:self.current])
        self._add_token(TokenType.NUMBER, value)

    def _string(self):
        """Processa strings."""
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()

        if self._is_at_end():
            raise LoxError(self.line, "String não terminada.")

        # Consome o '"' de fechamento
        self._advance()

        # Remove as aspas
        value = self.source[self.start + 1:self.current - 1]
        # Processa escapes básicos
        value = value.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        self._add_token(TokenType.STRING, value)

    def _match(self, expected: str) -> bool:
        """Verifica se o caractere atual é o esperado."""
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def _peek(self) -> str:
        """Retorna o caractere atual sem avançar."""
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def _peek_next(self) -> str:
        """Retorna o próximo caractere sem avançar."""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def _is_at_end(self) -> bool:
        """Verifica se chegamos ao final do código fonte."""
        return self.current >= len(self.source)

    def _advance(self) -> str:
        """Consome o próximo caractere."""
        self.current += 1
        return self.source[self.current - 1]

    def _add_token(self, token_type: TokenType, literal: Any = None):
        """Adiciona um token à lista."""
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))
