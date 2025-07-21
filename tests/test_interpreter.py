"""
Testes para o interpretador Lox.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lox.lexer import Lexer
from lox.parser import Parser
from lox.interpreter import Interpreter
import io
import contextlib


def capture_output(code):
    """Captura a saída de um código Lox."""
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(statements)
    return f.getvalue().strip()


def test_basic_arithmetic():
    """Testa operações aritméticas básicas."""
    result = capture_output('print 2 + 3;')
    assert result == "5"
    
    result = capture_output('print 10 - 4;')
    assert result == "6"
    
    result = capture_output('print 3 * 7;')
    assert result == "21"
    
    result = capture_output('print 15 / 3;')
    assert result == "5"
    
    print("✅ Testes de aritmética básica passaram")


def test_variables():
    """Testa variáveis."""
    code = """
    var a = 10;
    var b = 20;
    print a + b;
    """
    result = capture_output(code)
    assert result == "30"
    print("✅ Teste de variáveis passou")


def test_string_operations():
    """Testa operações com strings."""
    result = capture_output('print "Olá" + " " + "mundo";')
    assert result == "Olá mundo"
    
    result = capture_output('print "Número: " + 42;')
    assert result == "Número: 42"
    
    print("✅ Testes de strings passaram")


def test_arrays():
    """Testa arrays."""
    code = """
    var arr = [1, 2, 3];
    print arr[0];
    print arr[2];
    """
    result = capture_output(code)
    lines = result.split('\n')
    assert lines[0] == "1"
    assert lines[1] == "3"
    print("✅ Teste de arrays passou")


def test_conditionals():
    """Testa condicionais."""
    code = """
    var x = 5;
    if (x > 3) {
        print "maior";
    } else {
        print "menor";
    }
    """
    result = capture_output(code)
    assert result == "maior"
    print("✅ Teste de condicionais passou")


def test_loops():
    """Testa loops while."""
    code = """
    var i = 0;
    while (i < 3) {
        print i;
        i = i + 1;
    }
    """
    result = capture_output(code)
    lines = result.split('\n')
    assert lines == ["0", "1", "2"]
    print("✅ Teste de loops passou")


def test_builtin_functions():
    """Testa funções built-in."""
    result = capture_output('print length([1, 2, 3, 4]);')
    assert result == "4"
    
    result = capture_output('print type(42);')
    assert result == "number"
    
    result = capture_output('print type("hello");')
    assert result == "string"
    
    print("✅ Testes de funções built-in passaram")


if __name__ == "__main__":
    print("🧪 Executando testes do interpretador...")
    test_basic_arithmetic()
    test_variables()
    test_string_operations()
    test_arrays()
    test_conditionals()
    test_loops()
    test_builtin_functions()
    print("🎉 Todos os testes do interpretador passaram!")
