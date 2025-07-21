"""
Funções e classes built-in do interpretador Lox.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, List, Optional
from .lox_error import RuntimeError


class LoxCallable(ABC):
    """Interface para objetos que podem ser chamados (funções, classes)."""
    
    @abstractmethod
    def arity(self) -> int:
        """Retorna o número de argumentos esperados."""
        pass
    
    @abstractmethod
    def call(self, interpreter, arguments: List[Any]) -> Any:
        """Executa a chamada."""
        pass


class LoxFunction(LoxCallable):
    """Representa uma função definida pelo usuário."""
    
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def call(self, interpreter, arguments: List[Any]) -> Any:
        from .environment import Environment
        from .lox_error import ReturnException
        
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None
    
    def bind(self, instance):
        """Liga 'this' a uma instância específica."""
        from .environment import Environment
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)
    
    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"


class LoxClass(LoxCallable):
    """Representa uma classe Lox."""
    
    def __init__(self, name: str, superclass: Optional['LoxClass'], methods: dict):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()
    
    def call(self, interpreter, arguments: List[Any]) -> Any:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def find_method(self, name: str) -> Optional[LoxFunction]:
        """Encontra um método na classe ou superclasse."""
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.find_method(name)
        
        return None
    
    def __str__(self):
        return self.name


class LoxInstance:
    """Representa uma instância de uma classe Lox."""
    
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields = {}
    
    def get(self, name):
        """Obtém uma propriedade da instância."""
        from .token_types import Token
        
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        
        raise RuntimeError(name.line, f"Propriedade indefinida '{name.lexeme}'.")
    
    def set(self, name, value):
        """Define uma propriedade da instância."""
        self.fields[name.lexeme] = value
    
    def __str__(self):
        return f"{self.klass.name} instance"


class LoxArray:
    """Representa um array Lox."""
    
    def __init__(self, elements: List[Any]):
        self.elements = elements
    
    def get(self, index: int) -> Any:
        """Obtém um elemento do array."""
        if 0 <= index < len(self.elements):
            return self.elements[index]
        raise RuntimeError(0, f"Índice {index} fora dos limites do array.")
    
    def set(self, index: int, value: Any):
        """Define um elemento do array."""
        if 0 <= index < len(self.elements):
            self.elements[index] = value
        else:
            raise RuntimeError(0, f"Índice {index} fora dos limites do array.")
    
    def length(self) -> int:
        """Retorna o tamanho do array."""
        return len(self.elements)
    
    def append(self, value: Any):
        """Adiciona um elemento ao final do array."""
        self.elements.append(value)
    
    def __str__(self):
        return str(self.elements)


# === FUNÇÕES BUILT-IN ===

class ClockFunction(LoxCallable):
    """Função nativa que retorna o tempo atual."""
    
    def arity(self) -> int:
        return 0
    
    def call(self, interpreter, arguments: List[Any]) -> Any:
        return time.time()
    
    def __str__(self):
        return "<native fn>"


class LengthFunction(LoxCallable):
    """Função nativa que retorna o tamanho de um array ou string."""
    
    def arity(self) -> int:
        return 1
    
    def call(self, interpreter, arguments: List[Any]) -> Any:
        arg = arguments[0]
        if isinstance(arg, LoxArray):
            return float(arg.length())
        elif isinstance(arg, str):
            return float(len(arg))
        else:
            raise RuntimeError(0, "Argumento deve ser um array ou string.")
    
    def __str__(self):
        return "<native fn>"


class TypeFunction(LoxCallable):
    """Função nativa que retorna o tipo de um valor."""
    
    def arity(self) -> int:
        return 1
    
    def call(self, interpreter, arguments: List[Any]) -> Any:
        arg = arguments[0]
        if arg is None:
            return "nil"
        elif isinstance(arg, bool):
            return "boolean"
        elif isinstance(arg, float):
            return "number"
        elif isinstance(arg, str):
            return "string"
        elif isinstance(arg, LoxArray):
            return "array"
        elif isinstance(arg, LoxFunction):
            return "function"
        elif isinstance(arg, LoxClass):
            return "class"
        elif isinstance(arg, LoxInstance):
            return "instance"
        else:
            return "unknown"
    
    def __str__(self):
        return "<native fn>"


class StrFunction(LoxCallable):
    """Função nativa que converte um valor para string."""
    
    def arity(self) -> int:
        return 1
    
    def call(self, interpreter, arguments: List[Any]) -> Any:
        from .interpreter import stringify
        return stringify(arguments[0])
    
    def __str__(self):
        return "<native fn>"


# Dicionário com todas as funções built-in
BUILTIN_FUNCTIONS = {
    "clock": ClockFunction(),
    "length": LengthFunction(),
    "type": TypeFunction(),
    "str": StrFunction(),
}
