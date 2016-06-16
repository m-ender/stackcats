import argparse
from collections import defaultdict, deque
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

    def __iter__(self):
        return iter(self.stack)

    def __getitem__(self, index):
        return self.stack[index]


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
        if self.stack_num in self.stacks and not self.curr_stack:
            del self.stacks[self.stack_num]

        self.stack_num += offset
        self.curr_stack = self.stacks[self.stack_num]

    def move_left(self):
        self.move_by(-1)

    def move_right(self):
        self.move_by(1)

    def swap_stacks(self, num1, num2):
        self.stacks[num1], self.stacks[num2] = self.stacks[num2], self.stacks[num1]

        if num1 in self.stacks and not self.stacks[num1]:
            del self.stacks[num1]
            
        if num2 in self.stacks and not self.stacks[num2]:
            del self.stacks[num2]

        self.curr_stack = self.stacks[self.stack_num]

    def swap_left(self):
        self.swap_stacks(self.stack_num-1, self.stack_num)

    def swap_right(self):
        self.swap_stacks(self.stack_num+1, self.stack_num)

    def __len__(self):
        return len(self.curr_stack)

    def __str__(self):
        max_depth = max(map(len, self.stacks.values()))
        min_num = min(self.stacks.keys())
        max_num = max(self.stacks.keys())

        rows = []

        for i in range(max_depth+3):
            rows.append(["..."] if i == max_depth else ["   "])

        for n in range(min_num, max_num+1):
            stack = self.stacks[n] if n in self.stacks else []
            width = max(len(str(x)) for x in stack) if stack else 1

            rows[0].append(('v' if self.stack_num == n else ' ').rjust(width))
            rows[-1].append(('^' if self.stack_num == n else ' ').rjust(width))
            rows[-2].append('0'.rjust(width))

            for i in range(max_depth):
                rows[max_depth-i].append((str(stack[i]) if i < len(stack) else '').rjust(width))

        for i in range(max_depth+3):
            rows[i].append("..." if i == max_depth else "   ")

        return '\n'.join(' '.join(row).rstrip() for row in rows)


class StackCats():
    def __init__(self, code, debug_level=0, mirror_left=False, mirror_right=False,
          print_mirrored=False):
        code = code.splitlines()[0]

        if mirror_right:
            code = code + self.__mirror(code[:-1])
        elif mirror_left:
            code = self.__mirror(code[1:]) + code

        # Code potentially minus debug chars if debug options are set.
        program = code
        self.debug_level = debug_level

        if debug_level > 0:
            program = program.replace('"', '')

        if program != self.__mirror(program):
            self.error(InvalidCodeException, "program is not symmetric")

        self.code = code
        self.loop_targets = {}
        index_stack = []

        for i,c in enumerate(code):
            if c not in "(){}-!*_^:+=|T<>[]I/\\X" and (c != '"' or self.debug_level == 0):
                self.error(InvalidCodeException, 'invalid character in source code, {}'.format(c))

            if c in "{(":
                index_stack.append((i, c))

            elif c in "})":
                if not index_stack or c != self.__mirror(index_stack[-1][1]):
                    self.error(InvalidCodeException, "unmatched {}".format(c))

                start, _ = index_stack.pop()
                self.loop_targets[start] = i
                self.loop_targets[i] = start

        if index_stack:
            self.error(InvalidCodeException, "unmatched {}".format(index_stack[-1][1]))

        if print_mirrored:
            print(code, end='')


    def run(self, input_="", numeric_input=False, numeric_output=False, max_ticks=None):
        # Prepare tape, with initial input.
        self.tape = Tape()
        self.tape.push(-1)

        if numeric_input:
            for number in re.findall("[-+]?[0-9]+", input_)[::-1]:
                self.tape.push(int(number))
        else:
            for c in input_[::-1]:
                self.tape.push(ord(c))

        # Run code.
        self.loop_conditions = []       
        self.ip = 0
        self.tick = 0
        self.output = []

        while self.ip < len(self.code):
            if self.debug_level >= 2:
                self.print_debug()
            
            self.interpret(self.code[self.ip])
            self.ip += 1
            self.tick += 1

            if max_ticks is not None and self.tick >= max_ticks:
                self.error(TimeoutError, "program timed out")

        if self.debug_level >= 2:
            self.print_debug()

        # Output, ignoring any -1s at bottom.
        while self.tape:
            value = self.tape.pop()

            if value != -1 or self.tape:
                if numeric_output:
                    self.output.extend([str(value), '\n'])
                else:
                    self.output.append(chr(value % 256))

        self.output = ''.join(self.output)
        return self.output


    def interpret(self, instruction):
        self.execute_inst(instruction)
        self.tape.swallow_zeroes()


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
            self.tape.swap_right()
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

        elif instruction == '_':
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
            elif value > 0:
                self.tape.move_right()

            self.tape.push(-value)

        elif instruction == 'T':
            if self.tape.peek() != 0:
                self.tape.reverse()

        elif instruction == '"' and self.debug_level >= 1:
            self.print_debug()

    def print_debug(self):
        print(file=sys.stderr)
        print("Tick", self.tick, file=sys.stderr)
        print("Tape:", file=sys.stderr)
        print(self.tape, file=sys.stderr)
        print("Program:", file=sys.stderr)
        print(self.code, file=sys.stderr)
        print('^'.rjust(self.ip+1), file=sys.stderr)

    def error(self, exception, message):
        # Note: the error messages could mirror brackets as well, but that could get confusing.
        message = "Error: " + message
        raise exception(message + " | " + message[::-1])

    def __mirror(self, string):
        mirror_chars = dict(zip("(){}[]<>\\/", ")(}{][></\\"))
        return ''.join(mirror_chars.get(c, c) for c in string[::-1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest="debug1", help="debug level 1: print debug info at double quotes"
        " in code", action="store_true")
    parser.add_argument('-D', dest="debug2", help="debug level 2: print debug info at every tick",
        action="store_true")
    parser.add_argument('-l', dest="mirrored_left", help="expand source with first char at centre before"
        " executing", action="store_true")
    parser.add_argument('-L', dest="print_mirrored_left", help="prints source code mirorred left",
        action="store_true")
    parser.add_argument('-m', dest="mirrored_right", help="expand source with last char at centre before"
        " executing", action="store_true")
    parser.add_argument('-M', dest="print_mirrored_right", help="prints source code mirorred right",
        action="store_true")
    parser.add_argument('-i', dest="numeric_input", help="use numeric input", action="store_true")
    parser.add_argument('-o', dest="numeric_output", help="use numeric output", action="store_true")
    parser.add_argument('-n', dest="numeric", help="use numeric input and output",
        action="store_true")
    parser.add_argument('-t', dest="max_ticks", help="maximum number of ticks the program will try"
        " to run for", type=int)
    parser.add_argument("program_path", help="path to file containing program", type=str)

    # Open code file.
    args = parser.parse_args()

    with open(args.program_path) as codefile:
        code = codefile.read()

    # Read input from STDIN.
    input_ = ''.join(sys.stdin.readlines())

    # Debug flags.
    if args.debug1:
        debug_level = 1
    elif args.debug2:
        debug_level = 2
    else:
        debug_level = 0

    # Mirroring
    mirror_left = args.mirrored_left or args.print_mirrored_left
    mirror_right = args.mirrored_right or args.print_mirrored_right
    print_mirrored = args.print_mirrored_left or args.print_mirrored_right

    # Numeric I/O
    numeric_input = args.numeric or args.numeric_input
    numeric_output = args.numeric or args.numeric_output
    
    try:
        interpreter = StackCats(code, debug_level, mirror_left, mirror_right, print_mirrored)
    except InvalidCodeException as e:
        exit(e)

    if not print_mirrored:
        try:
            output = interpreter.run(input_, numeric_input, numeric_output, args.max_ticks)
            print(output, end='')
        except TimeoutError as e:
            exit(e)
        except KeyboardInterrupt as e:
            exit("^C")
