# Stack Cats

**Stack Cats** (abbreviated as **SKS**) is a stack-based, [reversible](https://en.wikipedia.org/wiki/Reversible_computing) (esoteric) programming language. It was originally conceived of [for a language-design challenge on Code Golf Stack Exchange](http://codegolf.stackexchange.com/q/61804/8478), but later designed and developed independently of that.

## Basics

Every program in Stack Cats is written on a single line, where each character is a command. Being a reversible programming language means that for every command there is a way to undo it. The language is designed such that any snippet of commands can be undone by *mirroring* it. This means that the string of commands is reversed and all characters that come in symmetric pairs are swapped (`()`, `{}`, `[]`, `<>`, `\/`). For instance, the snippet `>[[(!-)/` undoes the snippet `\(-!)]]<`. Therefore, Stack Cats programs are made up exclusively of characters which are either self-symmetric (in most fonts) like `-_|!:I` or which come in pairs, i.e. `(){}[]<>\/`. Note that from a theoretical standpoint, self-symmetric characters compute [involutions](https://en.wikipedia.org/wiki/Involution_(mathematics)), while symmetric pairs compute [bijections](https://en.wikipedia.org/wiki/Bijection) (and their inverses).

## Syntax

There are only two syntactic rules for Stack Cats:

1. Every valid program must have mirror symmetry. That is, if the entire program is mirrored (see above), it must remain unchanged. This has a few implications. a) Every Stack Cats program computes an involution on the global memory state (since every program is its own inverse). b) Every even-length program computes the identity (i.e. a [cat program](http://esolangs.org/wiki/Cat_program)) provided that it terminates, since the second half undoes the first. c) Every non-trivial program has odd length. If we call the command in the centre of the program `A`, then every such program has the structure `pAq`, where `p` is an arbitrary program and `q` computes its inverse. Note that `A` needs to be one of the self-symmetric characters, so it is itself an involution. Hence, programming in Stack Cats is about finding a function `p` which transforms a very simple involution `A` into the desired program.
2. Parentheses, `()`, and braces, `{}`, need to be balanced correctly, as they form loops. They can be nested arbitrarily but not interleaved like `({)}`. (`[]` and `<>` can appear individually and don't need be matched.)

## Memory model

Stack Cats operates on an infinite tape of stacks. The tape has a tape head which can be moved and points at the "current" stack. Commands tend to operate locally on or near the tape head. The stacks store arbitrary-precision (signed) integers and contain an implicit, infinite amount of zeros at the bottom. Initially, all stacks but the one where the tape head starts are empty (apart from those zeros).

## I/O

To ensure full reversibility, Stack Cats has no I/O commands, as these side-effects cannot be reversed cleanly. Instead, when the program starts, all input (which has to be finite) is read from the standard input stream. All the bytes are pushed onto the initial stack, with the first input byte on top and the last input byte at the bottom.

At the end of the program (provided it terminates), the contents of the current stack (pointed at by the tape head) are taken modulo 256 and printed as bytes to the standard output stream. Again, the value on top is used for the first byte and the value at the bottom is used for the last byte. Note that to print trailing null-bytes, you should use a multiple of 256 (other than zero), because all zeros at the bottom are assumed to be part of the implicit infinite pool of zeros and will not be printed.

## Commands

### Control Flow

Remember that `()` and `{}` always have to be balanced correctly.

- `(`: If the top of the current stack is zero or negative, jump past the matching `)`.
- `)`: If the top of the current stack is zero or negative, jump back past the matching `(`.
- `{`: Remembers the top of the current stack.
- `}`: If the top of the current stack differs from the value remembered at the matching `{`, jump back past the matching `{` (without remembering a new value).

In summary, `()` is a loop which is entered and left only when the top of the stack is positive, whereas `{}` is a loop which always iterates at least once and stops when the value from the beginning is seen again at the end of an iteration.

### Arithmetic

- `-`: Negate the top of the current stack (i.e. multiply by `-1`).
- `!`: Take the bitwise NOT of the top of the current stack (this is equivalent to incrementing and negating).
- `'`: Toggle the least-significant bit of the top of the current stack. In other words, compute `x XOR 1`.
- `_`: Pop `a`, pop `b`, push `b`, push `b - a`.
- `^`: Pop `a`, pop `b`, push `b`, push `b XOR a`.
- `T`: If the top of the current stack is positive, negate the value underneath.

### Stack manipulation

- `:`: Swap the top two elements of the current stack.
- `=`: Swap the top elements of the two adjacent stacks.
- `|`: Reverse all values on the current stack down to the first zero from the top.

### Movement and tape manipulation

- `<`: Move the tape head left one stack.
- `>`: Move the tape head right one stack.
- `[`: Move the tape head left one stack, taking the top of the current stack with it.
- `]`: Move the tape head right one stack, taking the top of the current stack with it.
- `I`: If the top of the current stack is negative, do `[-`, if it is positive, do `]-`, if it is zero, do nothing.
- `/`: Swap the current stack with the stack to the left, and move the tape head left.
- `\`: Swap the current stack with the stack to the right, and move the tape head right.
- `X`: Swap the stacks left and right of the current stack.