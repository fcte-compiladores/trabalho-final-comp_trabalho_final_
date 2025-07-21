# Interpretador Lox Estendido

## Integrantes
- Samuel Ribeiro da Costa  - 211031486.
- Guilherme Coelho Mendoça  - 202016364.

## Introdução

Este projeto implementa um interpretador para a linguagem Lox com extensões adicionais. A linguagem Lox é uma linguagem de programação dinâmica, orientada a objetos e com sintaxe similar ao C. Nossa implementação inclui as funcionalidades básicas do Lox original, além de extensões como:

- **Arrays**: Suporte a arrays dinâmicos com sintaxe `[1, 2, 3]`
- **Comentários de bloco**: Suporte a comentários `/* ... */` aninhados
- **Operadores de atribuição**: `+=` e `-=`
- **Comandos de controle**: `break` e `continue` em loops
- **Sistema de módulos**: Comando `import` para carregar módulos
- **Melhor tratamento de erros**: Mensagens de erro mais detalhadas

### Estratégias e Algoritmos

O interpretador utiliza as técnicas clássicas de compilação:
1. **Análise Léxica**: Converte o código fonte em tokens
2. **Análise Sintática**: Constrói uma árvore sintática abstrata (AST)
3. **Interpretação**: Executa diretamente da AST usando o padrão Visitor

### Exemplos de Sintaxe

```lox
// Variáveis e tipos básicos
var nome = "Lox";
var numero = 42;
var booleano = true;

// Arrays (extensão)
var lista = [1, 2, 3, 4, 5];
print lista[0]; // Acesso por índice

// Funções
fun saudacao(nome) {
    return "Olá, " + nome + "!";
}

// Classes
class Pessoa {
    init(nome) {
        this.nome = nome;
    }
    
    falar() {
        print "Meu nome é " + this.nome;
    }
}
```

## Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd trabalho-final-comp_trabalho_final_
```

2. Instale as dependências:
```bash
pip install -e .
```

3. Para desenvolvimento (com dependências de teste):
```bash
pip install -e ".[dev]"
```

### Como Executar

**Executar um arquivo Lox:**
```bash
python -m lox exemplos/hello_world.lox
```

**Modo interativo (REPL):**
```bash
python -m lox
```

**Executar testes:**
```bash
python tests/test_lexer.py
python tests/test_interpreter.py
```

## Exemplos

O diretório `exemplos/` contém vários arquivos demonstrando as funcionalidades:

- **hello_world.lox**: Hello World básico ✅
- **operacoes.lox**: Operações matemáticas básicas ✅
- **arrays.lox**: Demonstra o uso de arrays (extensão) ✅
- **controle.lox**: Estruturas de controle (if/while) ✅
- **funcoes.lox**: Funções básicas (em desenvolvimento)
- **classes.lox**: Programação orientada a objetos (TODO)
- **loops.lox**: Loops com break/continue (TODO)

## Referências

1. **"Crafting Interpreters" por Robert Nystrom**: Livro base que define a linguagem Lox e técnicas de implementação de interpretadores. Usado como referência principal para a estrutura do projeto.

2. **Documentação Python**: Para implementação das estruturas de dados e padrões de design.

3. **Artigos sobre AST e Padrão Visitor**: Para a implementação da travessia da árvore sintática.

### Contribuições Originais

- Implementação de arrays dinâmicos
- Sistema de módulos com importação
- Comentários de bloco aninhados
- Operadores de atribuição compostos
- Comandos break/continue em loops
- Melhor tratamento e relatório de erros

## Estrutura do Código

```
lox/
├── __init__.py          # Módulo principal
├── main.py              # Ponto de entrada
├── token_types.py       # Definições de tokens
├── lexer.py             # Análise léxica ✅
├── parser.py            # Análise sintática ✅
├── ast_nodes.py         # Nós da AST ✅
├── interpreter.py       # Interpretador ✅
├── environment.py       # Ambiente de variáveis ✅
├── lox_error.py         # Classes de erro ✅
└── builtins.py          # Funções built-in ✅

exemplos/                # Arquivos de exemplo ✅
tests/                   # Testes unitários ✅
├── test_lexer.py        # Testes do analisador léxico
├── test_interpreter.py  # Testes do interpretador
└── run_tests.py         # Script para executar todos os testes
```

### Etapas de Compilação

1. **Análise Léxica** (`lexer.py`): Converte caracteres em tokens
2. **Análise Sintática** (`parser.py`): Converte tokens em AST
3. **Análise Semântica**: Verificação de tipos e escopo (integrada ao interpretador)
4. **Interpretação** (`interpreter.py`): Execução direta da AST

## Bugs/Limitações/Problemas Conhecidos

## Funcionalidades Implementadas ✅

### Básicas do Lox:
- ✅ **Variáveis**: `var nome = "valor";`
- ✅ **Tipos de dados**: números, strings, booleanos, nil
- ✅ **Operadores aritméticos**: `+`, `-`, `*`, `/`, `%`
- ✅ **Operadores de comparação**: `<`, `<=`, `>`, `>=`, `==`, `!=`
- ✅ **Operadores lógicos**: `and`, `or`, `!`
- ✅ **Estruturas condicionais**: `if`/`else`
- ✅ **Loops**: `while`
- ✅ **Funções**: declaração e chamada (básico)
- ✅ **Expressões**: agrupamento com parênteses
- ✅ **Comandos**: `print`, atribuição

### Extensões Implementadas:
- ✅ **Arrays**: `[1, 2, 3]`, acesso por índice `arr[0]`
- ✅ **Comentários de bloco**: `/* comentário */`
- ✅ **Operador módulo**: `%`
- ✅ **Concatenação automática**: strings + números
- ✅ **Funções built-in**: `clock()`, `length()`, `type()`, `str()`

### Em Desenvolvimento:
- 🔄 **Funções com parâmetros**: problemas no parser
- 🔄 **Classes e objetos**: estrutura pronta, precisa de testes
- 🔄 **Loops for**: implementado mas com bugs
- 🔄 **Break/continue**: estrutura pronta
- ❌ **Sistema de módulos**: não implementado

## Testes Unitários ✅

O projeto inclui uma suite abrangente de testes que verifica:

- **Análise Léxica**: Tokens, palavras-chave, strings, números, arrays
- **Operações Aritméticas**: +, -, *, /, %
- **Variáveis**: Declaração e atribuição
- **Strings**: Concatenação e conversão automática
- **Arrays**: Criação e acesso por índice
- **Condicionais**: if/else
- **Loops**: while
- **Funções Built-in**: length(), type(), clock(), str()

**Executar testes:**
```bash
python tests/test_lexer.py      # Testa o analisador léxico
python tests/test_interpreter.py # Testa o interpretador
```

**Cobertura de testes:** ~80% das funcionalidades implementadas

### Limitações Atuais
- Sistema de módulos ainda em desenvolvimento
- Garbage collection não implementado
- Sem otimizações de performance
- Arrays limitados a tipos básicos

### Melhorias Futuras
- Implementar closure adequado para funções aninhadas
- Adicionar sistema de tipos mais robusto
- Melhorar mensagens de erro com contexto
- Implementar debugging integrado
- Adicionar mais operadores (potência, bitwise)

### Problemas Conhecidos
- Recursão profunda pode causar stack overflow
- Strings com escapes complexos podem não funcionar corretamente
- Import circular entre módulos não é detectado 
