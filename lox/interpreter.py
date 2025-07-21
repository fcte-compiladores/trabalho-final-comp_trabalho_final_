"""
Interpretador principal para a linguagem Lox.
"""

from typing import Any, List, Optional
from .ast_nodes import *
from .token_types import Token, TokenType
from .environment import Environment
from .lox_error import RuntimeError, ReturnException, BreakException, ContinueException
from .builtins import *


def stringify(value: Any) -> str:
    """Converte um valor Lox para string."""
    if value is None:
        return "nil"
    
    if isinstance(value, bool):
        return "true" if value else "false"
    
    if isinstance(value, float):
        text = str(value)
        if text.endswith(".0"):
            text = text[:-2]
        return text
    
    if isinstance(value, LoxArray):
        elements = [stringify(elem) for elem in value.elements]
        return "[" + ", ".join(elements) + "]"
    
    return str(value)


def is_truthy(value: Any) -> bool:
    """Determina se um valor é truthy em Lox."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return True


def is_equal(a: Any, b: Any) -> bool:
    """Verifica igualdade entre dois valores Lox."""
    if a is None and b is None:
        return True
    if a is None:
        return False
    return a == b


class Interpreter(ExprVisitor, StmtVisitor):
    """Interpretador que executa código Lox."""
    
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}
        
        # Adiciona funções built-in ao ambiente global
        for name, func in BUILTIN_FUNCTIONS.items():
            self.globals.define(name, func)
    
    def interpret(self, statements: List[Stmt]):
        """Interpreta uma lista de statements."""
        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeError as error:
            print(f"Erro de execução: {error}")
    
    def _execute(self, stmt: Stmt):
        """Executa um statement."""
        stmt.accept(self)
    
    def resolve(self, expr: Expr, depth: int):
        """Resolve uma variável local."""
        self.locals[expr] = depth
    
    def execute_block(self, statements: List[Stmt], environment: Environment):
        """Executa um bloco de statements em um novo ambiente."""
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous
    
    def _evaluate(self, expr: Expr) -> Any:
        """Avalia uma expressão."""
        return expr.accept(self)
    
    def _lookup_variable(self, name: Token, expr: Expr) -> Any:
        """Busca uma variável no ambiente correto."""
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)
    
    # === VISITOR METHODS FOR EXPRESSIONS ===
    
    def visit_assign_expr(self, expr: AssignExpr) -> Any:
        value = self._evaluate(expr.value)
        
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        
        return value
    
    def visit_binary_expr(self, expr: BinaryExpr) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)
        
        token_type = expr.operator.type
        
        if token_type == TokenType.GREATER:
            self._check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif token_type == TokenType.GREATER_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif token_type == TokenType.LESS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif token_type == TokenType.LESS_EQUAL:
            self._check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif token_type == TokenType.BANG_EQUAL:
            return not is_equal(left, right)
        elif token_type == TokenType.EQUAL_EQUAL:
            return is_equal(left, right)
        elif token_type == TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif token_type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            elif isinstance(left, str) or isinstance(right, str):
                return stringify(left) + stringify(right)
            elif isinstance(left, LoxArray) and isinstance(right, LoxArray):
                return LoxArray(left.elements + right.elements)
            else:
                raise RuntimeError(expr.operator.line, 
                                 "Operandos devem ser dois números, duas strings ou dois arrays.")
        elif token_type == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            if float(right) == 0:
                raise RuntimeError(expr.operator.line, "Divisão por zero.")
            return float(left) / float(right)
        elif token_type == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        elif token_type == TokenType.PERCENT:
            self._check_number_operands(expr.operator, left, right)
            return float(left) % float(right)
        
        return None
    
    def visit_call_expr(self, expr: CallExpr) -> Any:
        callee = self._evaluate(expr.callee)
        
        arguments = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))
        
        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren.line, "Só é possível chamar funções e classes.")
        
        if len(arguments) != callee.arity():
            raise RuntimeError(expr.paren.line, 
                             f"Esperado {callee.arity()} argumentos mas recebeu {len(arguments)}.")
        
        return callee.call(self, arguments)
    
    def visit_get_expr(self, expr: GetExpr) -> Any:
        obj = self._evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        
        raise RuntimeError(expr.name.line, "Apenas instâncias têm propriedades.")
    
    def visit_grouping_expr(self, expr: GroupingExpr) -> Any:
        return self._evaluate(expr.expression)
    
    def visit_literal_expr(self, expr: LiteralExpr) -> Any:
        return expr.value
    
    def visit_logical_expr(self, expr: LogicalExpr) -> Any:
        left = self._evaluate(expr.left)
        
        if expr.operator.type == TokenType.OR:
            if is_truthy(left):
                return left
        else:  # AND
            if not is_truthy(left):
                return left
        
        return self._evaluate(expr.right)
    
    def visit_set_expr(self, expr: SetExpr) -> Any:
        obj = self._evaluate(expr.object)
        
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(expr.name.line, "Apenas instâncias têm campos.")
        
        value = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value
    
    def visit_super_expr(self, expr: SuperExpr) -> Any:
        distance = self.locals.get(expr)
        superclass = self.environment.get_at(distance, "super")
        
        obj = self.environment.get_at(distance - 1, "this")
        
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeError(expr.method.line, 
                             f"Método indefinido '{expr.method.lexeme}'.")
        
        return method.bind(obj)
    
    def visit_this_expr(self, expr: ThisExpr) -> Any:
        return self._lookup_variable(expr.keyword, expr)
    
    def visit_unary_expr(self, expr: UnaryExpr) -> Any:
        right = self._evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            self._check_number_operand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not is_truthy(right)
        
        return None
    
    def visit_variable_expr(self, expr: VariableExpr) -> Any:
        return self._lookup_variable(expr.name, expr)
    
    def visit_array_expr(self, expr: ArrayExpr) -> Any:
        elements = []
        for element_expr in expr.elements:
            elements.append(self._evaluate(element_expr))
        return LoxArray(elements)
    
    def visit_index_expr(self, expr: IndexExpr) -> Any:
        obj = self._evaluate(expr.object)
        index = self._evaluate(expr.index)
        
        if isinstance(obj, LoxArray):
            if not isinstance(index, float):
                raise RuntimeError(expr.bracket.line, "Índice deve ser um número.")
            return obj.get(int(index))
        elif isinstance(obj, str):
            if not isinstance(index, float):
                raise RuntimeError(expr.bracket.line, "Índice deve ser um número.")
            idx = int(index)
            if 0 <= idx < len(obj):
                return obj[idx]
            else:
                raise RuntimeError(expr.bracket.line, "Índice fora dos limites da string.")
        
        raise RuntimeError(expr.bracket.line, "Apenas arrays e strings podem ser indexados.")
    
    def visit_index_set_expr(self, expr: IndexSetExpr) -> Any:
        obj = self._evaluate(expr.object)
        index = self._evaluate(expr.index)
        value = self._evaluate(expr.value)
        
        if isinstance(obj, LoxArray):
            if not isinstance(index, float):
                raise RuntimeError(expr.bracket.line, "Índice deve ser um número.")
            obj.set(int(index), value)
            return value
        
        raise RuntimeError(expr.bracket.line, "Apenas arrays podem ter elementos atribuídos por índice.")
    
    # === VISITOR METHODS FOR STATEMENTS ===
    
    def visit_block_stmt(self, stmt: BlockStmt):
        self.execute_block(stmt.statements, Environment(self.environment))
    
    def visit_class_stmt(self, stmt: ClassStmt):
        superclass = None
        if stmt.superclass is not None:
            superclass = self._evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name.line, "Superclasse deve ser uma classe.")
        
        self.environment.define(stmt.name.lexeme, None)
        
        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        
        methods = {}
        for method in stmt.methods:
            function = LoxFunction(method, self.environment, 
                                 method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        
        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        
        if superclass is not None:
            self.environment = self.environment.enclosing
        
        self.environment.assign(stmt.name, klass)
    
    def visit_expression_stmt(self, stmt: ExpressionStmt):
        self._evaluate(stmt.expression)
    
    def visit_function_stmt(self, stmt: FunctionStmt):
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)
    
    def visit_if_stmt(self, stmt: IfStmt):
        if is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)
    
    def visit_print_stmt(self, stmt: PrintStmt):
        value = self._evaluate(stmt.expression)
        print(stringify(value))
    
    def visit_return_stmt(self, stmt: ReturnStmt):
        value = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)
        
        raise ReturnException(value)
    
    def visit_var_stmt(self, stmt: VarStmt):
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)
    
    def visit_while_stmt(self, stmt: WhileStmt):
        try:
            while is_truthy(self._evaluate(stmt.condition)):
                try:
                    self._execute(stmt.body)
                except ContinueException:
                    continue
        except BreakException:
            pass
    
    def visit_break_stmt(self, stmt: BreakStmt):
        raise BreakException()
    
    def visit_continue_stmt(self, stmt: ContinueStmt):
        raise ContinueException()
    
    # === UTILITY METHODS ===
    
    def _check_number_operand(self, operator: Token, operand: Any):
        """Verifica se o operando é um número."""
        if not isinstance(operand, float):
            raise RuntimeError(operator.line, "Operando deve ser um número.")
    
    def _check_number_operands(self, operator: Token, left: Any, right: Any):
        """Verifica se ambos operandos são números."""
        if not isinstance(left, float) or not isinstance(right, float):
            raise RuntimeError(operator.line, "Operandos devem ser números.")
