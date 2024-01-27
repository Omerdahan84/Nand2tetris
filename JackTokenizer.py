"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        self.clean_lines(input_stream)
        # Saved keywords regular expression
        # Changed: added \b for bound
        self.keywords_regex = r'\b(?:class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b'
        # saved symbols regular expression
        self.symbols_regex = r'\s*\{|\}\s*|\s*\(\s*|\s*\)\s*|\s*\[\s*|\s*\]\s*|\s*\.\s*|\s*,\s*|\s*;\s*|\s*\+\s*|\s*-\s*|\s*\*\s*|\s*/\s*|\s*&\s*|\s*<\s*|\s*>\s*|\s*=\s*|\s*~\s*|\s*\|\s*'

        # Identifier regular expression
        # CHANGED: z in first [] to uppercase
        self.identifier_regex = r'[a-zA-Z_][a-zA-Z0-9_]*'
        # Interger regular expression
        self.integer_regex = r'\d+'
        # String constants regular expression
        # ORIGINAK self.string_regex = r'"[^\n]*"'
        self.string_regex = r'"[^\n]*"'
        # Token index
        self.token_index = 0
        # tokenize the first line
        self.tokenize_lines()

    # CHANGED: DEAL WITH MULTILINE DIFFERENT
    def clean_lines(self, input_stream) -> None:
        """clean the input file from comments and space
        """
        self.input_lines = input_stream.read().splitlines()
        # Remove white space

        # remove comments inline comment
        self.input_lines = [self.relevantline(line)
                            for line in self.input_lines]
        # remove leading space
        self.input_lines = [line.lstrip().rstrip()
                            for line in self.input_lines]

        # removing empty lines
        self.input_lines = [
            line for line in self.input_lines if (line != "" and line is not None and line != " ")]
        # remove multiline comments
        self.remove_multiline_comments()
        # removing empty lines
        self.input_lines = [
            line for line in self.input_lines if (line != "" and line is not None and line != " ")]

    def remove_comments(self):
        inside_multiline_comment = False
        inside_string = False
        cleaned_lines = []
        for line in self.input_lines:
            if '"' in line:
                inside_string = True
                for i in range(len(line)):

            if not inside_multiline_comment and not inside_string:
                # case where the start and end is in the same line
                if ("/*" in line or "/**") and "*/" in line:
                    # if there is a multi line comment and code inside one line
                    for i in range(len(line) - 1):
                        if line[i] == "/" and line[i + 1] == "*":
                            start = i
                            continue
                        if line[i] == "*" and line[i + 1] == "/":
                            end = i
                    line = line[:start] + line[end + 2:]
                    cleaned_lines.append(line)

                    continue
                # Check for the start of multiline comment
                if "/*" in line or "/**" in line:
                    inside_multiline_comment = True
                    # Handle the case where the start of the multiline comment is on the same line as code
                    line = line[:line.find("/*")]
            if not inside_multiline_comment:
                cleaned_lines.append(line)
            # Check for the end of multiline comment
            if inside_multiline_comment and "*/" in line:
                inside_multiline_comment = False
                # Handle the case where the end of the multiline comment is on the same line as code
                cleaned_lines.append(line[line.find("*/") + 2:])
        self.input_lines = cleaned_lines

    def tokenize_lines(self) -> None:
        """Take a line from the input file and breaks it down to tokens

        Args:
            line (str): the line to separate 
        """
        # using all the patterns
        combined_pattern = re.compile(
            self.keywords_regex + '|' + self.symbols_regex + '|' + self.identifier_regex + '|' + self.string_regex + '|' + self.integer_regex)
        self.token_list = [combined_pattern.findall(
            line) for line in self.input_lines]
        # making the list of list into one list
        # Also note that four of the symbols used in the Jack language (<, >, and &) are also used for XML markup, and thus they cannot appear verbatim as XML data. To solve the problem, we require the tokenizer to output these tokens as &lt;, &gt;, and &amp;
        values_to_replace = ["<", ">", "&"]
        replacement_dict = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}
        self.token_list = [
            replacement_dict[token.strip()] if token.strip() in values_to_replace else token.strip() for tokens in
            self.token_list for token in tokens]

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.token_index < len(self.token_list)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # checks if we pooped all the tokens in the current line

        if self.has_more_tokens():
            self.token_index += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        token = self.current_token()

        if re.match(self.keywords_regex, token):
            return "KEYWORD"
        if re.match(self.symbols_regex, token):
            return "SYMBOL"
        if re.match(self.identifier_regex, token):
            return "IDENTIFIER"
        if re.match(self.integer_regex, token):
            return "INT_CONST"
        if re.match(self.string_regex, token):
            return "STRING_CONST"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token().upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        special_op = {"<": "&lt;", ">": "&gt;", '"': "&quot", "&": "&amp;"}
        if self.current_token() in special_op:
            return special_op[self.current_token()]
        return self.current_token()

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self.current_token()

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return self.current_token()

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!

        return self.current_token().replace('"', '')

    ################### EXTRA METHODS NOT PART OF THE ORIGINAL API###########

    def relevantline(self, line) -> str:
        """return only the relevant part of the line the includes the op

        Args:
            line (str): the line to tream

        Returns:
            str: the line after the comment is removed
        """
        # search for block comment
        # end = line.find("/*")
        # if end!=-1:
        #     return line[:end]

        # searching for line cooments
        end = line.find("//")

        # checking if the comment is inside a string
        start_string = len(line) - 1
        end_string = len(line) - 1
        inside_string = False
        for i in range(len(line)):
            if line[i] == '"' and not inside_string:
                start_string = i
                inside_string = True
                continue
            if line[i] == '"' and inside_string:
                end_string = i
                break

        # if end < start_string we have something like // "this is comment" need to take regular
        if end != -1 and end < start_string:
            return line[:end]
        # if start_string < end < end_string the comment is inside the string, need to return regulary
        if end != -1 and start_string < end and end <end_string:
            return  line

        if end != -1 and end > end_string and end >= start_string:
            return line[:end]

        return line

    def current_token(self) -> str:
        return self.token_list[self.token_index]

    # try to see the next token, if no more tokens return false.
    def peek_ahead(self):
        if self.token_index + 1 >= len(self.token_list):
            return False
        return self.token_list[self.token_index + 1]
