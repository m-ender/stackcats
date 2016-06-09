import argparse
from collections import defaultdict, deque
from enum import Enum
import re
import sys


class InvalidCodeException(Exception):
    pass


class BottomlessStack():
    def __init__(self):
        self.stack = deque()

    def push(self, value):
        self.stack.append(value)
        self.swallow_zeroes()

    def pop(self):
        if self.stack:
            return self.stack.pop()

        return 0

    def peek(self):
        if self.stack:
            return self.stack[-1]

        return 0

    def reverse(self):
        self.stack.reverse()
        self.swallow_zeroes()

    def swallow_zeroes(self):
        while self.stack and self.stack[0] == 0:
            self.stack.popleft()

    def __len__(self):
        return len(self.stack)


class Tape():
    def __init__(self):
        self.stacks = defaultdict(BottomlessStack)
        self.stack_num = 0
        self.curr_stack = self.stacks[self.stack_num]

    def push(self, value):
        self.curr_stack.push(value)

    def pop(self):
        return self.curr_stack.pop()

    def peek(self):
        return self.curr_stack.peek()

    def reverse(self):
        self.curr_stack.reverse()

    def swallow_zeroes(self):
        self.curr_stack.swallow_zeroes()

    def move_by(self, offset):
        if not self.curr_stack:
            del self.stacks[self.stack_num]

        self.stack_num += offset
        self.curr_stack = self.stacks[self.stack_num]

    def move_left(self):
        self.move_by(-1)

    def move_right(self):
        self.move_by(1)

    def swap_stacks(self, num1, num2):
        self.stacks[num1], self.stacks[num2] = self.stacks[num2], self.stacks[num1]

        if not self.stacks[num1]: del self.stacks[num1]
        if not self.stacks[num2]: del self.stacks[num2]

    def swap_left(self):
        self.swap_stacks(self.stack_num-1, self.stack_num)

    def swap_right(self):
        self.swap_stacks(self.stack_num-1, self.stack_num)

    def __len__(self):
        return len(self.curr_stack)


class DebugFlags(Enum):
    # Flags correspond to specific bits, and so are multiples of 2.
    PRINT_AT_QUOTES = 1
    PRINT_EVERY_TICK = 2


class StackCats():
    def __init__(self, code, debug=0, mirrored=False, print_mirrored=False):
        # Check code validity
        pairs = "([{<\/>}])"
        pair_dict = dict(zip(pairs, pairs[::-1]))

        if mirrored or print_mirrored:
            code = code + ''.join(pair_dict.get(c, c) for c in code[:-1][::-1])

        self.code = code
        self.debug = debug

        for i in range(len(code)//2):
            char = self.code[i]
            if pair_dict.get(char, char) != self.code[~i]:
                raise InvalidCodeException("Code must be convenient palindromic")

        if len(code) % 2 == 1 and self.code[len(code)//2] in pairs:
            raise InvalidCodeException("Centre char cannot be part of a char pair.")

        self.loop_targets = {}
        index_stack = []

        for i,c in enumerate(code):
            if c in "{(":
                index_stack.append((i, c))

            elif c in "})":
                if not index_stack or c != pair_dict[index_stack[-1][1]]:
                    raise InvalidCodeException("Mismatched loop brackets")

                start, _ = index_stack.pop()
                self.loop_targets[start] = i
                self.loop_targets[i] = start

        if print_mirrored:
            print(code, end='')


    def run(self, input_="", numeric_input=False, numeric_output=False):
        # Prepare tape, with initial input.
        self.tape = Tape()
        self.tape.push(-1)

        if numeric_input:
            for number in re.findall("[-+]?[0-9]+", input_)[::-1]:
                self.tape.push(number)
        else:
            for c in input_[::-1]:
                self.tape.push(ord(c))

        # Run code.
        self.loop_conditions = []       
        self.ip = 0

        while self.ip < len(self.code):
            self.interpret(self.code[self.ip])
            self.ip += 1

        # Output, ignoring any -1s at bottom.
        while self.tape:
            value = self.tape.pop()

            if value != -1 or self.tape:
                if numeric_output:
                    print(value)
                else:
                    sys.stdout.write(chr(value % 256))


    def interpret(self, instruction):
        ip = self.ip

        self.execute_inst(instruction)
        self.tape.swallow_zeroes()

        if self.debug & DebugFlags.PRINT_EVERY_TICK.value:
            self.print_debug()


    def execute_inst(self, instruction):
        # Symmetric pairs
        if instruction == '(':
            if self.tape.peek() < 1:
                self.ip = self.loop_targets[self.ip]

        elif instruction == ')':
            if self.tape.peek() < 1:
                self.ip = self.loop_targets[self.ip]

        elif instruction == '/':
            self.tape.swap_left()
            self.tape.move_left()

        elif instruction == '\\':
            self.tape_swap_right()
            self.tape.move_right()

        elif instruction == '<':
            self.tape.move_left()

        elif instruction == '>':
            self.tape.move_right()

        elif instruction == '[':
            value = self.tape.pop()
            self.tape.move_left()
            self.tape.push(value)

        elif instruction == ']':
            value = self.tape.pop()
            self.tape.move_right()
            self.tape.push(value)

        elif instruction == '{':
            self.loop_conditions.append(self.tape.peek())

        elif instruction == '}':
            if self.tape.peek() == self.loop_conditions[-1]:
                self.loop_conditions.pop()
            else:
                self.ip = self.loop_targets[self.ip]

        # Self-symmetric characters
        # Arithmetic
        elif instruction == '!':
            self.tape.push(~self.tape.pop())

        elif instruction == '-':
            self.tape.push(-self.tape.pop())

        elif instruction == '*':
            self.tape.push(self.tape.pop() ^ 1)

        elif instruction == '^':
            value = self.tape.pop()
            self.tape.push(self.tape.peek() ^ value)

        elif instruction == '-':
            value = self.tape.pop()
            self.tape.push(self.tape.peek() - value)

        elif instruction == ':':
            top, bottom = self.tape.pop(), self.tape.pop()
            self.tape.push(top)
            self.tape.push(bottom)

        elif instruction == '+':
            top, middle, bottom = self.tape.pop(), self.tape.pop(), self.tape.pop()
            self.tape.push(top)
            self.tape.push(middle)
            self.tape.push(bottom)

        elif instruction == '|':
            values = []

            while self.tape.peek() != 0:
                values.append(self.tape.pop())

            for v in values:
                self.tape.push(v)

        elif instruction == '=':
            self.tape.move_left()
            x = self.tape.pop()
            self.tape.move_right()
            self.tape.move_right()
            y = self.tape.pop()
            self.tape.push(x)
            self.tape.move_left()
            self.tape.move_left()
            self.tape.push(y)
            self.tape.move_right()

        elif instruction == 'X':
            self.tape.swap_left()
            self.tape.swap_right()
            self.tape.swap_left()

        elif instruction == 'I':
            value = self.tape.pop()

            if value < 0:
                self.tape.move_left()
            else:
                self.tape.move_right()

            self.tape.push(-value)

        elif instruction == 'T':
            if self.tape.peek() != 0:
                self.tape.reverse()

        elif instruction == '"' and self.debug & DebugFlags.PRINT_AT_QUOTES.value:
            self.print_debug()

    def print_debug():
        # TODO: Implement printing debug information.
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest="debug1", help="debug level 1: print debug info at double quotes"
        " in code", action="store_true")
    parser.add_argument('-D', dest="debug2", help="debug level 2: print debug info at every tick",
        action="store_true")
    parser.add_argument('-m', dest="mirrored", help="mirror mode: source is expanded with last char at"
        "centre before executing", action="store_true")
    parser.add_argument('-M', dest="print_mirrored", help="prints source code mirorred",
        action="store_true")
    parser.add_argument("program_path", help="path to file containing program", type=str)

    # Open code file.
    args = parser.parse_args()

    with open(args.program_path) as codefile:
        code = codefile.read()

    # Read input from STDIN.
    input_ = ''.join(sys.stdin.readlines())

    # Check flags.
    if args.debug2:
        debug_level = 2
    elif args.debug1:
        debug_level = 1
    else:
        debug_level = 0
    
    try:
        interpreter = StackCats(code, debug_level, args.mirrored, args.print_mirrored)
    except InvalidCodeException as e:
        exit(e)

    if not args.print_mirrored:
        interpreter.run(input_)
