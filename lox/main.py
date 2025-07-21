"""
Ponto de entrada principal do interpretador Lox.
"""

import sys
from pathlib import Path
from lox.lexer import Lexer
from lox.parser import Parser
from lox.interpreter import Interpreter
from lox.lox_error import LoxError, ParseError


# Interpretador global
interpreter = Interpreter()


def run_file(path: str):
    """Executa um arquivo Lox."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            source = file.read()
        run(source)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{path}' não encontrado.")
        sys.exit(74)
    except LoxError as e:
        print(e)
        sys.exit(65)


def run_prompt():
    """Executa o interpretador em modo interativo."""
    print("Lox Interpreter v0.1.0")
    print("Digite 'exit' para sair.")
    
    while True:
        try:
            line = input("> ")
            if line.strip() == "exit":
                break
            run(line)
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break
        except (LoxError, ParseError) as e:
            print(e)


def run(source: str):
    """Executa código Lox."""
    try:
        # Análise léxica
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        # Análise sintática
        parser = Parser(tokens)
        statements = parser.parse()
        
        # Interpretação
        interpreter.interpret(statements)
        
    except LoxError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro interno: {e}")


def main():
    """Função principal."""
    if len(sys.argv) > 2:
        print("Uso: python -m lox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()


if __name__ == "__main__":
    main()
