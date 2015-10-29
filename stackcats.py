import argparse
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

    def __len__(self):
        return len(self.stack)

    def __repr__(self):
        return repr(self.stack)


class StackCats():
    def __init__(self, code, trace=False):
        self.code = code
        self.trace = trace

        # Check code validity
        pairs = "([{<\/>}])"
        validity_dict = dict(zip(pairs, pairs[::-1]))

        for i in range(len(code)//2):
            char = self.code[i]
            if validity_dict.get(char, char) != self.code[~i]:
                raise InvalidCodeException("Code must be convenient palindromic")

        if len(code) % 2 == 1 and self.code[len(code)//2] in pairs:
            raise InvalidCodeException("Centre char cannot be part of a char pair.")


        self.loop_stack = [] # First half, [[ip, count]]
        self.loop_count = None # Second half
        self.loop_map = {}
        index_stack = []

        for i,c in enumerate(code):
            if len(code) % 2 == 1 and i == len(code)//2 and index_stack:
                raise InvalidCodeException("No loops through centre")

            if c == "{":
                index_stack.append(i)

            elif c == "}":
                if not index_stack:
                    raise InvalidCodeException("Mismatched loops brackets")

                start = index_stack.pop()
                self.loop_map[start] = i
                self.loop_map[i] = start - 1

        if index_stack:
            # Should not be reachable but just in case
            raise InvalidCodeException("Mismatched loops brackets")

    def run(self, input_=""):
        self.stack_tape = defaultdict(BottomlessStack)

        self.stack_num = 0
        self.stack_tape[self.stack_num] = BottomlessStack(map(ord, input_[::-1]))
        self.curr_stack = self.stack_tape[self.stack_num]

        self.memory_stack = BottomlessStack()
        
        self.ip = 0

        while self.ip < len(self.code):
            self.interpret(self.code[self.ip], self.ip < (len(self.code)+1)//2)
            self.ip += 1

        while self.curr_stack:
            sys.stdout.write(chr(self.pop() % 256))

    def interpret(self, instruction, first_half):
        self.execute_inst(instruction, first_half)
        self.curr_stack.swallow_zeroes()

        if self.trace:
            stack_str = ["{}: {}".format(n, self.stack_tape[n])
                         for n in sorted(self.stack_tape)]

            print("{:4d}  {}  {{{}}}".format(self.ip, instruction,
                      ", ".join(stack_str)), file=sys.stderr)

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

        elif instruction == "_":
            if first_half:
                self.push(0)
            else:
                self.pop()

        elif instruction == "#":
            if first_half:
                self.push(self.len())
            else:
                self.pop()

        elif instruction in "lr":
            mul = 1 if (instruction == "r") else -1
            
            if first_half:
                self.memory_stack.push(self.len())

                while self.curr_stack:
                    self.stack_tape[self.stack_num + mul*self.len()].push(self.pop())

            else:
                length = self.memory_stack.pop()

                if length >= 0:
                    stack_offsets = range(1, length+1)
                else:
                    stack_offsets = range(-1, length-1, -1)

                for n in stack_offsets:
                    self.push(self.stack_tape[self.stack_num + mul*n].pop())

        elif instruction == "{":
            if first_half:
                if not self.loop_stack or self.loop_stack[-1][0] != self.ip:
                    self.loop_stack.append([self.ip, 0])
                else:
                    self.loop_stack[-1][1] += 1

                cond = self.pop()
                self.push(cond)

                if cond <= 0:
                    self.ip = self.loop_map[self.ip]
                    self.memory_stack.push(self.loop_stack.pop()[1])

            else:
                if self.loop_count is None:
                    self.loop_count = self.memory_stack.pop()
                else:
                    self.loop_count -= 1

                if self.loop_count <= 0:
                    self.ip = self.loop_map[self.ip]
                    self.loop_count = None

        elif instruction == "}":
            self.ip = self.loop_map[self.ip]

                
    def pop(self):
        return self.curr_stack.pop()

    def push(self, elem):
        self.curr_stack.push(elem)

    def len(self):
        return len(self.curr_stack)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--trace', help="trace every step", action="store_true")
    parser.add_argument("program_path", help="path to file containing program",
                        type=str)
    parser.add_argument("input_path", nargs='?', help="path to file containing input",
                        type=str, default=None)

    args = parser.parse_args()

    with open(args.program_path) as codefile:
        code = codefile.read()

    if args.input_path:
        with open(args.input_path) as inputfile:
            input_ = inputfile.read()

    else:
        input_ = ""

    interpreter = StackCats(code, args.trace)
    interpreter.run(input_)
