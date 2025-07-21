"""
Testes para o lexer do interpretador Lox.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lox.lexer import Lexer
from lox.token_types import TokenType, Token
from lox.lox_error import LoxError


def test_single_character_tokens():
    """Testa tokens de um caractere."""
    source = "(){},.-+;*"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    expected_types = [
        TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN,
        TokenType.LEFT_BRACE, TokenType.RIGHT_BRACE,
        TokenType.COMMA, TokenType.DOT, TokenType.MINUS,
        TokenType.PLUS, TokenType.SEMICOLON, TokenType.STAR,
        TokenType.EOF
    ]
    
    actual_types = [token.type for token in tokens]
    assert actual_types == expected_types
    print("✅ Teste de tokens de um caractere passou")


def test_string_literals():
    """Testa strings."""
    source = '"Olá mundo"'
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].literal == "Olá mundo"
    print("✅ Teste de strings passou")


def test_number_literals():
    """Testa números."""
    source = "123 45.67"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].literal == 123.0
    assert tokens[1].type == TokenType.NUMBER
    assert tokens[1].literal == 45.67
    print("✅ Teste de números passou")


def test_identifiers_and_keywords():
    """Testa identificadores e palavras-chave."""
    source = "var foo = true;"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    expected_types = [
        TokenType.VAR, TokenType.IDENTIFIER, TokenType.EQUAL,
        TokenType.TRUE, TokenType.SEMICOLON, TokenType.EOF
    ]
    
    actual_types = [token.type for token in tokens]
    assert actual_types == expected_types
    print("✅ Teste de palavras-chave passou")


def test_arrays():
    """Testa sintaxe de arrays."""
    source = "[1, 2, 3]"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    expected_types = [
        TokenType.LEFT_BRACKET, TokenType.NUMBER, TokenType.COMMA,
        TokenType.NUMBER, TokenType.COMMA, TokenType.NUMBER,
        TokenType.RIGHT_BRACKET, TokenType.EOF
    ]
    
    actual_types = [token.type for token in tokens]
    assert actual_types == expected_types
    print("✅ Teste de arrays passou")


if __name__ == "__main__":
    print("🧪 Executando testes do lexer...")
    test_single_character_tokens()
    test_string_literals()
    test_number_literals()
    test_identifiers_and_keywords()
    test_arrays()
    print("🎉 Todos os testes do lexer passaram!")
