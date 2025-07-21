"""
Script para executar todos os testes do interpretador Lox.
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importa os módulos de teste
import test_lexer
import test_interpreter


def run_all_tests():
    """Executa todos os testes disponíveis."""
    print("🚀 Iniciando bateria de testes do Interpretador Lox...")
    print("=" * 50)
    
    try:
        # Testa o lexer
        print("\n📝 Testando Lexer...")
        test_lexer.test_single_character_tokens()
        test_lexer.test_string_literals()
        test_lexer.test_number_literals()
        test_lexer.test_identifiers_and_keywords()
        test_lexer.test_arrays()
        
        # Testa o interpretador
        print("\n🔧 Testando Interpretador...")
        test_interpreter.test_basic_arithmetic()
        test_interpreter.test_variables()
        test_interpreter.test_string_operations()
        test_interpreter.test_arrays()
        test_interpreter.test_conditionals()
        test_interpreter.test_loops()
        test_interpreter.test_builtin_functions()
        
        print("\n" + "=" * 50)
        print("🎉 TODOS OS TESTES PASSARAM! 🎉")
        print("📊 Cobertura de testes:")
        print("  - Análise Léxica: ✅")
        print("  - Operações Aritméticas: ✅")
        print("  - Variáveis: ✅")
        print("  - Strings: ✅")
        print("  - Arrays: ✅")
        print("  - Condicionais: ✅")
        print("  - Loops: ✅")
        print("  - Funções Built-in: ✅")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
