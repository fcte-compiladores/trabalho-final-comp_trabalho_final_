"""
Analisador sintático (Parser) para a linguagem Lox.
Implementa um parser recursivo descendente.
"""

from typing import List, Optional, Any
from .token_types import Token, TokenType
from .ast_nodes import *
from .lox_error import ParseError


class Parser:
    """Parser recursivo descendente para Lox."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> List[Stmt]:
        """Analisa os tokens e retorna uma lista de statements."""
        statements = []
        while not self._is_at_end():
            try:
                stmt = self._declaration()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                print(f"Erro de parse: {e}")
                self._synchronize()
        return statements
    
    # === DECLARATIONS ===
    
    def _declaration(self) -> Optional[Stmt]:
        """declaration → classDecl | funDecl | varDecl | statement"""
        try:
            if self._match(TokenType.CLASS):
                return self._class_declaration()
            if self._match(TokenType.FUN):
                return self._function("function")
            if self._match(TokenType.VAR):
                return self._var_declaration()
            return self._statement()
        except ParseError:
            self._synchronize()
            return None
    
    def _class_declaration(self) -> Stmt:
        """classDecl → "class" IDENTIFIER ( "<" IDENTIFIER )? "{" function* "}" """
        name = self._consume(TokenType.IDENTIFIER, "Esperado nome da classe.")
        
        superclass = None
        if self._match(TokenType.LESS):
            self._consume(TokenType.IDENTIFIER, "Esperado nome da superclasse.")
            superclass = VariableExpr(self._previous())
        
        self._consume(TokenType.LEFT_BRACE, "Esperado '{' antes do corpo da classe.")
        
        methods = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            methods.append(self._function("method"))
        
        self._consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo da classe.")
        return ClassStmt(name, superclass, methods)
    
    def _function(self, kind: str) -> FunctionStmt:
        """function → IDENTIFIER "(" parameters? ")" block"""
        name = self._consume(TokenType.IDENTIFIER, f"Esperado nome da {kind}.")
        
        self._consume(TokenType.LEFT_PAREN, f"Esperado '(' após nome da {kind}.")
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            parameters.append(self._consume(TokenType.IDENTIFIER, "Esperado nome do parâmetro."))
            while self._match(TokenType.COMMA):
                if len(parameters) >= 255:
                    raise ParseError(self._peek().line, "Não pode ter mais de 255 parâmetros.")
                parameters.append(self._consume(TokenType.IDENTIFIER, "Esperado nome do parâmetro."))
        
        self._consume(TokenType.RIGHT_PAREN, "Esperado ')' após parâmetros.")
        self._consume(TokenType.LEFT_BRACE, f"Esperado '{{' antes do corpo da {kind}.")
        body = self._block()
        
        return FunctionStmt(name, parameters, body)
    
    def _var_declaration(self) -> Stmt:
        """varDecl → "var" IDENTIFIER ( "=" expression )? ";" """
        name = self._consume(TokenType.IDENTIFIER, "Esperado nome da variável.")
        
        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Esperado ';' após declaração de variável.")
        return VarStmt(name, initializer)
    
    # === STATEMENTS ===
    
    def _statement(self) -> Stmt:
        """statement → exprStmt | forStmt | ifStmt | printStmt | returnStmt | whileStmt | breakStmt | continueStmt | block"""
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.BREAK):
            return self._break_statement()
        if self._match(TokenType.CONTINUE):
            return self._continue_statement()
        if self._match(TokenType.LEFT_BRACE):
            return BlockStmt(self._block())
        
        return self._expression_statement()
    
    def _for_statement(self) -> Stmt:
        """forStmt → "for" "(" ( varDecl | exprStmt | ";" ) expression? ";" expression? ")" statement"""
        self._consume(TokenType.LEFT_PAREN, "Esperado '(' após 'for'.")
        
        # Inicializador
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()
        
        # Condição
        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._consume(TokenType.SEMICOLON, "Esperado ';' após condição do loop.")
        
        # Incremento
        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Esperado ')' após cláusulas do for.")
        
        body = self._statement()
        
        # Desaçucaramento: transformar for em while
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])
        
        if condition is None:
            condition = LiteralExpr(True)
        body = WhileStmt(condition, body)
        
        if initializer is not None:
            body = BlockStmt([initializer, body])
        
        return body
    
    def _if_statement(self) -> Stmt:
        """ifStmt → "if" "(" expression ")" statement ( "else" statement )?"""
        self._consume(TokenType.LEFT_PAREN, "Esperado '(' após 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Esperado ')' após condição do if.")
        
        then_branch = self._statement()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._statement()
        
        return IfStmt(condition, then_branch, else_branch)
    
    def _print_statement(self) -> Stmt:
        """printStmt → "print" expression ";" """
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Esperado ';' após valor.")
        return PrintStmt(value)
    
    def _return_statement(self) -> Stmt:
        """returnStmt → "return" expression? ";" """
        keyword = self._previous()
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Esperado ';' após valor de retorno.")
        return ReturnStmt(keyword, value)
    
    def _while_statement(self) -> Stmt:
        """whileStmt → "while" "(" expression ")" statement"""
        self._consume(TokenType.LEFT_PAREN, "Esperado '(' após 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Esperado ')' após condição.")
        body = self._statement()
        
        return WhileStmt(condition, body)
    
    def _break_statement(self) -> Stmt:
        """breakStmt → "break" ";" """
        keyword = self._previous()
        self._consume(TokenType.SEMICOLON, "Esperado ';' após 'break'.")
        return BreakStmt(keyword)
    
    def _continue_statement(self) -> Stmt:
        """continueStmt → "continue" ";" """
        keyword = self._previous()
        self._consume(TokenType.SEMICOLON, "Esperado ';' após 'continue'.")
        return ContinueStmt(keyword)
    
    def _expression_statement(self) -> Stmt:
        """exprStmt → expression ";" """
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Esperado ';' após expressão.")
        return ExpressionStmt(expr)
    
    def _block(self) -> List[Stmt]:
        """block → "{" declaration* "}" """
        statements = []
        
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())
        
        self._consume(TokenType.RIGHT_BRACE, "Esperado '}' após bloco.")
        return statements
    
    # === EXPRESSIONS ===
    
    def _expression(self) -> Expr:
        """expression → assignment"""
        return self._assignment()
    
    def _assignment(self) -> Expr:
        """assignment → ( call "." )? IDENTIFIER ( "=" | "+=" | "-=" ) assignment | logic_or"""
        expr = self._or()
        
        if self._match(TokenType.EQUAL, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL):
            equals = self._previous()
            value = self._assignment()
            
            if isinstance(expr, VariableExpr):
                name = expr.name
                if equals.type == TokenType.PLUS_EQUAL:
                    value = BinaryExpr(expr, Token(TokenType.PLUS, "+", None, equals.line), value)
                elif equals.type == TokenType.MINUS_EQUAL:
                    value = BinaryExpr(expr, Token(TokenType.MINUS, "-", None, equals.line), value)
                return AssignExpr(name, value)
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.object, expr.name, value)
            elif isinstance(expr, IndexExpr):
                return IndexSetExpr(expr.object, expr.index, value, expr.bracket)
            
            raise ParseError(equals.line, "Alvo de atribuição inválido.")
        
        return expr
    
    def _or(self) -> Expr:
        """logic_or → logic_and ( "or" logic_and )*"""
        expr = self._and()
        
        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._and()
            expr = LogicalExpr(expr, operator, right)
        
        return expr
    
    def _and(self) -> Expr:
        """logic_and → equality ( "and" equality )*"""
        expr = self._equality()
        
        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._equality()
            expr = LogicalExpr(expr, operator, right)
        
        return expr
    
    def _equality(self) -> Expr:
        """equality → comparison ( ( "!=" | "==" ) comparison )*"""
        expr = self._comparison()
        
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _comparison(self) -> Expr:
        """comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )*"""
        expr = self._term()
        
        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, 
                           TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _term(self) -> Expr:
        """term → factor ( ( "-" | "+" ) factor )*"""
        expr = self._factor()
        
        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _factor(self) -> Expr:
        """factor → unary ( ( "/" | "*" | "%" ) unary )*"""
        expr = self._unary()
        
        while self._match(TokenType.SLASH, TokenType.STAR, TokenType.PERCENT):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpr(expr, operator, right)
        
        return expr
    
    def _unary(self) -> Expr:
        """unary → ( "!" | "-" ) unary | call"""
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._previous()
            right = self._unary()
            return UnaryExpr(operator, right)
        
        return self._call()
    
    def _call(self) -> Expr:
        """call → primary ( "(" arguments? ")" | "." IDENTIFIER | "[" expression "]" )*"""
        expr = self._primary()
        
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Esperado nome da propriedade após '.'.")
                expr = GetExpr(expr, name)
            elif self._match(TokenType.LEFT_BRACKET):
                index = self._expression()
                bracket = self._consume(TokenType.RIGHT_BRACKET, "Esperado ']' após índice.")
                expr = IndexExpr(expr, index, bracket)
            else:
                break
        
        return expr
    
    def _finish_call(self, callee: Expr) -> Expr:
        """arguments → expression ( "," expression )*"""
        arguments = []
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._expression())
            while self._match(TokenType.COMMA):
                if len(arguments) >= 255:
                    raise ParseError(self._peek().line, "Não pode ter mais de 255 argumentos.")
                arguments.append(self._expression())
        
        paren = self._consume(TokenType.RIGHT_PAREN, "Esperado ')' após argumentos.")
        return CallExpr(callee, paren, arguments)
    
    def _primary(self) -> Expr:
        """primary → "true" | "false" | "nil" | "this" | NUMBER | STRING | IDENTIFIER | "(" expression ")" | "[" elements? "]" | "super" "." IDENTIFIER"""
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        
        if self._match(TokenType.NIL):
            return LiteralExpr(None)
        
        if self._match(TokenType.THIS):
            return ThisExpr(self._previous())
        
        if self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._previous().literal)
        
        if self._match(TokenType.SUPER):
            keyword = self._previous()
            self._consume(TokenType.DOT, "Esperado '.' após 'super'.")
            method = self._consume(TokenType.IDENTIFIER, "Esperado nome do método da superclasse.")
            return SuperExpr(keyword, method)
        
        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._previous())
        
        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Esperado ')' após expressão.")
            return GroupingExpr(expr)
        
        # Array literal
        if self._match(TokenType.LEFT_BRACKET):
            elements = []
            if not self._check(TokenType.RIGHT_BRACKET):
                elements.append(self._expression())
                while self._match(TokenType.COMMA):
                    elements.append(self._expression())
            
            self._consume(TokenType.RIGHT_BRACKET, "Esperado ']' após elementos do array.")
            return ArrayExpr(elements)
        
        raise ParseError(self._peek().line, "Esperado expressão.")
    
    # === UTILITY METHODS ===
    
    def _match(self, *types: TokenType) -> bool:
        """Verifica se o token atual é de algum dos tipos dados."""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Retorna true se o token atual é do tipo dado."""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Consome o token atual e retorna ele."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Verifica se chegamos ao final dos tokens."""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Retorna o token atual."""
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Retorna o token anterior."""
        return self.tokens[self.current - 1]
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consome um token do tipo esperado ou lança erro."""
        if self._check(token_type):
            return self._advance()
        
        current_token = self._peek()
        raise ParseError(current_token.line, f"{message} Encontrado: {current_token.type.name}")
    
    def _synchronize(self):
        """Recupera de um erro de parse."""
        self._advance()
        
        while not self._is_at_end():
            if self._previous().type == TokenType.SEMICOLON:
                return
            
            if self._peek().type in [
                TokenType.CLASS, TokenType.FUN, TokenType.VAR,
                TokenType.FOR, TokenType.IF, TokenType.WHILE,
                TokenType.PRINT, TokenType.RETURN
            ]:
                return
            
            self._advance()
