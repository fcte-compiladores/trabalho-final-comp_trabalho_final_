"""
Classes de erro personalizadas para o interpretador Lox.
"""


class LoxError(Exception):
    """Erro base do interpretador Lox."""
    
    def __init__(self, line: int, message: str):
        self.line = line
        self.message = message
        super().__init__(f"[linha {line}] Erro: {message}")


class ParseError(LoxError):
    """Erro de análise sintática."""
    pass


class RuntimeError(LoxError):
    """Erro de tempo de execução."""
    pass


class ReturnException(Exception):
    """Exceção especial para implementar return."""
    
    def __init__(self, value):
        self.value = value
        super().__init__()


class BreakException(Exception):
    """Exceção especial para implementar break."""
    pass


class ContinueException(Exception):
    """Exceção especial para implementar continue."""
    pass
