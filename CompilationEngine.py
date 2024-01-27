"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
#FIXME : can't deal with multiline comments properly

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    XML_dict = {"KEYWORD": "keyword", "SYMBOL": "symbol", "IDENTIFIER": "identifier",
                "INT_CONST": "integerConstant", "STRING_CONST": "stringConstant"}
    binary_op_set = {"+", "-", "*", "/", "&amp;", "&lt;", "&gt;", "|", "="}
    unary_op_set = {"-", "~"}

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokenizer = input_stream
        self.indent = ""
        self.outFile = output_stream
        self.current_process = []

    ############################## GENERAL HELPER METHODS ##############################
    # add indent to the XML txt file
    def add_indent(self):
        self.indent += "  "

    # remove indent from the XML text file
    def remove_indent(self):
        self.indent = self.indent[:-2]

    # write the start of non-terminal rule
    def write_non_terminal_start(self, rule):
        self.current_process.append(rule)
        self.outFile.write(self.indent + "<" + rule + ">\n")
        self.add_indent()

    # write the end of wnd-terminal rule
    def write_non_terminal_end(self):
        self.remove_indent()
        self.outFile.write(self.indent + "</" + self.current_process.pop() + ">\n")

    # write terminal rule
    def write_terminal(self):
        self.outFile.write(self.indent + "<" + self.XML_dict[self.tokenizer.token_type()] + "> " +
                           self.tokenizer.current_token() + " </" + self.XML_dict[
                               self.tokenizer.token_type()] + ">" + "\n")
        self.tokenizer.advance()

    def write_string_const(self):
        self.outFile.write(self.indent + "<" + self.XML_dict[self.tokenizer.token_type()] + "> " +
                           self.tokenizer.string_val() + " </" + self.XML_dict[
                               self.tokenizer.token_type()] + ">" + "\n")
        self.tokenizer.advance()

    ############################## GENERAL HELPER METHODS END ##############################
    ##############################        API METHODS         ##############################
    ##############################    CLASS COMPILER HELPER   ##############################
    # check if variables declaration for the class exist
    def var_classdec_exist(self):
        if self.tokenizer.current_token() in ("static", "field"):
            return True
        return False

    # check if there is a declaration for the class subroutines
    def sub_routine_dec_exist(self):
        if self.tokenizer.current_token() in ("constructor", "function", "method"):
            return True
        return False

    # check if parameter list is empty
    def parameter_list_exist(self):
        if self.tokenizer.current_token() == ')':
            return False
        return True

    # #check if variables declaration for a sub routine  exist
    def var_routine_dec_exist(self):
        if self.tokenizer.current_token() != "var":
            return False
        return True

    # check if there is statement
    def statement_exist(self):
        if self.tokenizer.current_token() in ("let", "if", "while", "do","return"):
            return True
        return False

    # check if there is a statement start in the subroutine body
    def subroutine_body_exist(self):
        if self.tokenizer.current_token() == '}':
            return False
        return True

    # check if expression continue/ exist
    def expression_exist(self):
        current_token = self.tokenizer.current_token()
        return current_token in self.binary_op_set or current_token in self.unary_op_set

    # check if the current if has else
    def exist_else(self):
        return self.tokenizer.current_token() == "else"

    ##############################       CLASS COMPILER      ##############################
    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.write_non_terminal_start("class")  # write class tag
        # write class name tag
        self.write_terminal()
        # write class name
        self.write_terminal()
        # move to declared variables
        self.write_terminal()
        # write class varDec
        if self.var_classdec_exist():
            self.compile_class_var_dec()

        # write class subroutine Dec
        if self.sub_routine_dec_exist():
            self.compile_subroutine()

        # write the class closing "}"
        self.write_terminal()

        self.write_non_terminal_end()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!

        while self.var_classdec_exist():
            # write start of varDec
            self.write_non_terminal_start("classVarDec")
            while self.tokenizer.current_token() != ';':
                self.write_terminal()
            self.write_terminal()
            # write end of varDec
            self.write_non_terminal_end()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!

        while self.sub_routine_dec_exist():
            self.write_non_terminal_start("subroutineDec")
            # wrtie function type,name,name
            for i in range(4):
                self.write_terminal()
            # write closing ) for parameter list
            self.compile_parameter_list()
            self.write_terminal()

            # write function body
            self.write_non_terminal_start("subroutineBody")
            # write open { for function body
            self.write_terminal()

            if self.var_routine_dec_exist():
                self.compile_var_dec()
            if self.subroutine_body_exist():
                self.compile_statements()
            # write closing }  for function body
            self.write_terminal()
            # advance to next token
            self.write_non_terminal_end()
            self.write_non_terminal_end()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.write_non_terminal_start("parameterList")
        while self.parameter_list_exist():
            self.write_terminal()
        self.write_non_terminal_end()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!

        while self.var_routine_dec_exist():
            self.write_non_terminal_start("varDec")
            while self.tokenizer.current_token() != ';':
                self.write_terminal()
            # write the ; in the end of declaration + # advance to see if there is more declarations
            self.write_terminal()
            self.write_non_terminal_end()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!

        self.write_non_terminal_start("statements")
        while self.statement_exist():
            if self.tokenizer.current_token() == "do":
                self.compile_do()
            if self.tokenizer.current_token() == "while":
                self.compile_while()
            if self.tokenizer.current_token() == "let":
                self.compile_let()
            if self.tokenizer.current_token() == "if":
                self.compile_if()
            if self.tokenizer.current_token() == "return":
                self.compile_return()
        self.write_non_terminal_end()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.write_non_terminal_start("doStatement")
        # write the do keyword
        self.write_terminal()
        # write the subroutine call
        self.compile_subroutine_call()
        # write closing ";"
        self.write_terminal()
        self.write_non_terminal_end()

    """
    Sub routine helper
    """

    # CHANGED: before printed the "; "in the end
    def compile_subroutine_call(self):
        #  write until start of expression list
        while self.tokenizer.current_token() != '(':
            self.write_terminal()
        # write open '('
        self.write_terminal()
        # compile the expression list
        self.compile_expression_list()
        # write closing ')'

        self.write_terminal()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        # if there is an expression, compile it
        self.write_non_terminal_start("letStatement")
        # write the let and continue
        self.write_terminal()
        # compile var name
        self.write_terminal()
        if self.tokenizer.current_token() == '[':
            self.write_array_index()

        # write the = and continue
        self.write_terminal()
        # compile the expression
        self.compile_expression()
        # wrtie the ; in the end

        self.write_terminal()

        self.write_non_terminal_end()

    ##############################  Helper #########################################
    def write_array_index(self):
        # compile the open [
        self.write_terminal()
        self.compile_expression()
        # compile the closing ]
        self.write_terminal()

    ##############################  API continue #########################################
    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.write_non_terminal_start("whileStatement")
        # wrtie while keyword
        self.write_terminal()
        # write open "("
        self.write_terminal()
        # write while expression
        self.compile_expression()
        # write closing ")"
        self.write_terminal()
        # write open "{"
        self.write_terminal()
        self.compile_statements()
        # write closing "}"
        self.write_terminal()
        self.write_non_terminal_end()

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.write_non_terminal_start("returnStatement")
        # compile the return keyword
        self.write_terminal()
        while self.tokenizer.current_token() != ';':
            self.compile_expression()
        # compile ';' in the end
        self.write_terminal()
        self.write_non_terminal_end()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.write_non_terminal_start("ifStatement")
        # compile if key word"
        self.write_terminal()
        # compile open "("
        self.write_terminal()
        # compile the if expression
        self.compile_expression()
        # compile closing ")"
        self.write_terminal()
        # compile open "{"
        self.write_terminal()
        # compile if statements
        self.compile_statements()
        # compile closing "}"
        self.write_terminal()
        if self.exist_else():
            # compile the "else {"
            self.write_terminal()
            self.write_terminal()
            self.compile_statements()
            # compile closing "}"
            self.write_terminal()
        self.write_non_terminal_end()

    def compile_expression(self) -> None:

        """Compiles an expression."""
        # Your code goes here!
        # expression composed of term (binaryOp term)*
        self.write_non_terminal_start("expression")
        self.compile_term()
        while self.tokenizer.current_token() in self.binary_op_set:
            # write the binary op
            self.write_terminal()
            self.compile_term()

        self.write_non_terminal_end()

    # CHANGED compiled the last char
    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        self.write_non_terminal_start("term")
        # if there is '(' or '.' need to compile subroutinecall
        if self.tokenizer.token_type() == "IDENTIFIER" and (
                self.tokenizer.peek_ahead() == "(" or self.tokenizer.peek_ahead() == "."):
            self.compile_subroutine_call()
        # if there is '[' need to compile array
        elif self.tokenizer.current_token() in self.unary_op_set:
            # compile the unaryOp
            self.write_terminal()
            self.compile_term()
        elif self.tokenizer.peek_ahead() == "(":
            # compile open (
            self.write_terminal()
            self.compile_expression()
            # compile close )
            self.write_terminal()
        elif self.tokenizer.peek_ahead() == "[":
            # compile the varname
            self.write_terminal()
            # compile the open "["
            self.write_terminal()
            self.compile_expression()
            # compile the closing ]
            self.write_terminal()
        # check if this is not an unary op

        elif self.tokenizer.token_type() == "STRING_CONST":
            self.write_string_const()
        elif self.tokenizer.current_token() == "(":
            # compile open "("
            self.write_terminal()
            self.compile_expression()
            # compile closing ")"
            self.write_terminal()

        else:
            # compile terminal token
            self.write_terminal()
        self.write_non_terminal_end()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.write_non_terminal_start("expressionList")
        while self.parameter_list_exist():
            # if the current token is ',' write is as  a symbol
            if self.tokenizer.current_token() == ',':
                self.write_terminal()

            self.compile_expression()

        self.write_non_terminal_end()
