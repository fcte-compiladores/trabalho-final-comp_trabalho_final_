"""
Nós da Árvore Sintática Abstrata (AST) para o interpretador Lox.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional
from .token_types import Token


class ASTNode(ABC):
    """Classe base para todos os nós da AST."""
    pass


class Expr(ASTNode):
    """Classe base para expressões."""
    
    @abstractmethod
    def accept(self, visitor):
        pass


class Stmt(ASTNode):
    """Classe base para statements."""
    
    @abstractmethod
    def accept(self, visitor):
        pass


# === EXPRESSÕES ===

class AssignExpr(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_assign_expr(self)


class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_expr(self)


class CallExpr(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_call_expr(self)


class GetExpr(Expr):
    def __init__(self, object: Expr, name: Token):
        self.object = object
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_get_expr(self)


class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)


class LiteralExpr(Expr):
    def __init__(self, value: Any):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_literal_expr(self)


class LogicalExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_logical_expr(self)


class SetExpr(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr):
        self.object = object
        self.name = name
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_set_expr(self)


class SuperExpr(Expr):
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method
    
    def accept(self, visitor):
        return visitor.visit_super_expr(self)


class ThisExpr(Expr):
    def __init__(self, keyword: Token):
        self.keyword = keyword
    
    def accept(self, visitor):
        return visitor.visit_this_expr(self)


class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_unary_expr(self)


class VariableExpr(Expr):
    def __init__(self, name: Token):
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_variable_expr(self)


# === EXTENSÕES: Arrays ===

class ArrayExpr(Expr):
    def __init__(self, elements: List[Expr]):
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_array_expr(self)


class IndexExpr(Expr):
    def __init__(self, object: Expr, index: Expr, bracket: Token):
        self.object = object
        self.index = index
        self.bracket = bracket
    
    def accept(self, visitor):
        return visitor.visit_index_expr(self)


class IndexSetExpr(Expr):
    def __init__(self, object: Expr, index: Expr, value: Expr, bracket: Token):
        self.object = object
        self.index = index
        self.value = value
        self.bracket = bracket
    
    def accept(self, visitor):
        return visitor.visit_index_set_expr(self)


# === STATEMENTS ===

class BlockStmt(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_block_stmt(self)


class ClassStmt(Stmt):
    def __init__(self, name: Token, superclass: Optional[VariableExpr], methods: List['FunctionStmt']):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def accept(self, visitor):
        return visitor.visit_class_stmt(self)


class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)


class FunctionStmt(Stmt):
    def __init__(self, name: Token, params: List[Token], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_function_stmt(self)


class IfStmt(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def accept(self, visitor):
        return visitor.visit_if_stmt(self)


class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_print_stmt(self)


class ReturnStmt(Stmt):
    def __init__(self, keyword: Token, value: Optional[Expr]):
        self.keyword = keyword
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_return_stmt(self)


class VarStmt(Stmt):
    def __init__(self, name: Token, initializer: Optional[Expr]):
        self.name = name
        self.initializer = initializer
    
    def accept(self, visitor):
        return visitor.visit_var_stmt(self)


class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_while_stmt(self)


# === EXTENSÕES: Controle de fluxo ===

class BreakStmt(Stmt):
    def __init__(self, keyword: Token):
        self.keyword = keyword
    
    def accept(self, visitor):
        return visitor.visit_break_stmt(self)


class ContinueStmt(Stmt):
    def __init__(self, keyword: Token):
        self.keyword = keyword
    
    def accept(self, visitor):
        return visitor.visit_continue_stmt(self)


# === VISITOR PATTERN ===

class ExprVisitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: AssignExpr): pass
    
    @abstractmethod
    def visit_binary_expr(self, expr: BinaryExpr): pass
    
    @abstractmethod
    def visit_call_expr(self, expr: CallExpr): pass
    
    @abstractmethod
    def visit_get_expr(self, expr: GetExpr): pass
    
    @abstractmethod
    def visit_grouping_expr(self, expr: GroupingExpr): pass
    
    @abstractmethod
    def visit_literal_expr(self, expr: LiteralExpr): pass
    
    @abstractmethod
    def visit_logical_expr(self, expr: LogicalExpr): pass
    
    @abstractmethod
    def visit_set_expr(self, expr: SetExpr): pass
    
    @abstractmethod
    def visit_super_expr(self, expr: SuperExpr): pass
    
    @abstractmethod
    def visit_this_expr(self, expr: ThisExpr): pass
    
    @abstractmethod
    def visit_unary_expr(self, expr: UnaryExpr): pass
    
    @abstractmethod
    def visit_variable_expr(self, expr: VariableExpr): pass
    
    @abstractmethod
    def visit_array_expr(self, expr: ArrayExpr): pass
    
    @abstractmethod
    def visit_index_expr(self, expr: IndexExpr): pass
    
    @abstractmethod
    def visit_index_set_expr(self, expr: IndexSetExpr): pass


class StmtVisitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt: BlockStmt): pass
    
    @abstractmethod
    def visit_class_stmt(self, stmt: ClassStmt): pass
    
    @abstractmethod
    def visit_expression_stmt(self, stmt: ExpressionStmt): pass
    
    @abstractmethod
    def visit_function_stmt(self, stmt: FunctionStmt): pass
    
    @abstractmethod
    def visit_if_stmt(self, stmt: IfStmt): pass
    
    @abstractmethod
    def visit_print_stmt(self, stmt: PrintStmt): pass
    
    @abstractmethod
    def visit_return_stmt(self, stmt: ReturnStmt): pass
    
    @abstractmethod
    def visit_var_stmt(self, stmt: VarStmt): pass
    
    @abstractmethod
    def visit_while_stmt(self, stmt: WhileStmt): pass
    
    @abstractmethod
    def visit_break_stmt(self, stmt: BreakStmt): pass
    
    @abstractmethod
    def visit_continue_stmt(self, stmt: ContinueStmt): pass
