from collections import defaultdict
import sys

class InvalidCodeException(Exception):
    pass

class BottomlessStack():
    def __init__(self, default=None):
        if default:
            self.stack = list(default)
        else:
            self.stack = []

    def push(self, elem):
        self.stack.append(elem)
        self.swallow_zeroes()

    def pop(self):
        if self.stack:
            return self.stack.pop()

        return 0

    def swallow_zeroes(self):
        while self.stack and self.stack[0] == 0:
            self.stack = self.stack[1:]

    def __repr__(self):
        return repr(self.stack)

class StackCats():
    def __init__(self, code):
        self.code = code

        # Check code validity
        validity_dict = dict(zip("()[]{}<>\\/", ")(][}{></\\"))

        for i in range(len(code)//2):
            char = self.code[i]
            if validity_dict.get(char, char) != self.code[~i]:
                raise InvalidCodeException()

    def run(self, input_=""):
        self.stack_tape = defaultdict(BottomlessStack)

        self.stack_num = 0
        self.curr_stack = self.stack_tape[self.stack_num] = BottomlessStack(map(ord, input_))

        self.memory_stack = BottomlessStack()
        
        self.ip = 0

        while self.ip < len(self.code):
            self.interpret(self.code[self.ip], self.ip < (len(self.code)+1)//2)
            self.ip += 1

    def interpret(self, instruction, first_half):
        self.execute_inst(instruction, first_half)
        self.curr_stack.swallow_zeroes()

        print(self.stack_tape) # For debugging

    def execute_inst(self, instruction, first_half):        
        if instruction == "(":
            elem = self.pop()
            self.push(elem - 1)
        
        elif instruction == ")":
            elem = self.pop()
            self.push(elem + 1)

        elif instruction == "<":
            self.stack_num -= 1
            self.curr_stack = self.stack_tape[self.stack_num]

        elif instruction == ">":
            self.stack_num += 1   
            self.curr_stack = self.stack_tape[self.stack_num]

        elif instruction == "[":
            if first_half:
                elem = self.pop()
                self.stack_tape[self.stack_num-1].push(elem)
            else:
                elem = self.stack_tape[self.stack_num+1].pop()
                self.push(elem)            

        elif instruction == "]":
            if first_half:
                elem = self.pop()
                self.stack_tape[self.stack_num+1].push(elem)
            else:
                elem = self.stack_tape[self.stack_num-1].pop()
                self.push(elem)

        elif instruction == ":":
            if first_half:
                elem = self.pop()
                self.push(elem)
                self.push(elem)
            else:
                self.pop()

        elif instruction == ";":
            if first_half:
                elem = self.pop()
                self.memory_stack.push(elem)
            else:
                elem = self.memory_stack.pop()
                self.push(elem)

        elif "0" <= instruction <= "9":
            if first_half:
                elem = self.pop()
                n = int(instruction)
                self.push(10*elem + n)
            else:
                elem = self.pop()
                self.push(elem//10)
                

    def pop(self):
        return self.curr_stack.pop()

    def push(self, elem):
        self.curr_stack.push(elem)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: py -3 stackcats.py <code file> [input file]")

    with open(sys.argv[1]) as codefile:
        code = codefile.read()

    if len(sys.argv) == 2:
        input_ = ""
    else:
        with open(sys.argv[2]) as inputfile:
            input_ = inputfile.read()

    interpreter = StackCats(code)
    interpreter.run(input_)
