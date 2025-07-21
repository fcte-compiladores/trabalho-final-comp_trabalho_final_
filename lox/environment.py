"""
Ambiente de execução para variáveis do interpretador Lox.
"""

from typing import Any, Dict, Optional
from .token_types import Token
from .lox_error import RuntimeError


class Environment:
    """Ambiente de execução que gerencia variáveis e escopo."""
    
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any):
        """Define uma nova variável no ambiente."""
        self.values[name] = value
    
    def get(self, name: Token) -> Any:
        """Obtém o valor de uma variável."""
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise RuntimeError(name.line, f"Variável indefinida '{name.lexeme}'.")
    
    def assign(self, name: Token, value: Any):
        """Atribui um valor a uma variável existente."""
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(name.line, f"Variável indefinida '{name.lexeme}'.")
    
    def get_at(self, distance: int, name: str) -> Any:
        """Obtém uma variável a uma distância específica na cadeia de escopos."""
        return self._ancestor(distance).values.get(name)
    
    def assign_at(self, distance: int, name: Token, value: Any):
        """Atribui a uma variável a uma distância específica na cadeia de escopos."""
        self._ancestor(distance).values[name.lexeme] = value
    
    def _ancestor(self, distance: int) -> 'Environment':
        """Retorna o ambiente ancestral a uma distância específica."""
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        return environment
