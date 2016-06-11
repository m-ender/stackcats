# Stack Cats

**Stack Cats** (abbreviated as **SKS**) is a stack-based, [reversible](https://en.wikipedia.org/wiki/Reversible_computing) (esoteric) programming language. It was originally conceived of [for a language-design challenge on Code Golf Stack Exchange](http://codegolf.stackexchange.com/q/61804/8478), but later designed and developed independently of that.

## Basics

Every program in Stack Cats is written on a single line, where each character is a command. Being a reversible programming language means that for every command there is a way to undo it. The language is designed such that any snippet of commands can be undone by *mirroring* it. This means that the string of commands is reversed and all characters that come in symmetric pairs are swapped (`()`, `{}`, `[]`, `<>`, `\/`). For instance, the snippet `>[[(!-)/` undoes the snippet `\(-!)]]<`. Therefore, Stack Cats programs are made up exclusively of characters which are either self-symmetric (in most fonts) like `-_|!:I` or which come in pairs, i.e. `(){}[]<>\/`. Note that from a theoretical standpoint, self-symmetric characters compute [involutions](https://en.wikipedia.org/wiki/Involution_(mathematics)), while symmetric pairs compute [bijections](https://en.wikipedia.org/wiki/Bijection) (and their inverses).

## Syntax

As stated above, Stack Cats programs are written on a single line. However, source files may contain additional lines for comments or command-line instructions. Everything starting at the first newline is ignored by the interpreter.

Beyond that there are only two syntactic rules for Stack Cats:

1. Every valid program must have mirror symmetry. That is, if the entire program is mirrored (see above), it must remain unchanged. This has a few implications. a) Every Stack Cats program computes an involution on the global memory state (since every program is its own inverse). b) Every even-length program computes the identity (i.e. a [cat program](http://esolangs.org/wiki/Cat_program)) provided that it terminates, since the second half undoes the first. c) Every non-trivial program has odd length. If we call the command in the centre of the program `A`, then every such program has the structure `pAq`, where `p` is an arbitrary program and `q` computes its inverse. Note that `A` needs to be one of the self-symmetric characters, so it is itself an involution. Hence, programming in Stack Cats is about finding a function `p` which transforms a very simple involution `A` into the desired program.
2. Parentheses, `()`, and braces, `{}`, need to be balanced correctly, as they form loops. They can be nested arbitrarily but not interleaved like `({)}`. (`[]` and `<>` can appear individually and don't need be matched.)

Note that using unknown characters (i.e. any which don't correspond to a command) will result in an error at the start of the program.

## Memory model

Stack Cats operates on an infinite tape of stacks. The tape has a tape head which can be moved and points at the "current" stack. Commands tend to operate locally on or near the tape head. The stacks store arbitrary-precision (signed) integers and contain an implicit, infinite amount of zeros at the bottom. Initially, all stacks but the one where the tape head starts are empty (apart from those zeros).

Note that any zeros on top of this implicit pool of zeros are not distinguishable from it by any means. Therefore, in the remainder of this document "the bottom of the stack" always refers to the last non-zero value on the stack.

## I/O

To ensure full reversibility, Stack Cats has no I/O commands, as these side-effects cannot be reversed cleanly. Instead, when the program starts, all input (which has to be finite) is read from the standard input stream. A `-1` is pushed on the initial stack, and then all the bytes from the input are pushed, with the first input byte on top and the last input byte at the bottom (just above the `-1`).

At the end of the program (provided it terminates), the contents of the current stack (pointed at by the tape head) are taken modulo 256 and printed as bytes to the standard output stream. Again, the value on top is used for the first byte and the value at the bottom is used for the last byte. If the value at the very bottom is `-1`, it is ignored. In order to print trailing null bytes you can either put a `-1` below them, or you can use any non-zero multiple of 256 which are also printed as null-bytes.

## Execution Options

Every specification-compliant interpreter should provide the following options for executing Stack Cats programs:

- For input, read decimal signed integers instead of bytes. If this option is used, the input is scanned for numbers matching the regular expression `[-+]?[0-9]+` and push those instead of byte values. (Still with a `-1` at the bottom.)
- For output, print decimal signed integers instead of bytes. Every integer is followed by a single linefeed (0x0A). (Still, an optional `-1` at the bottom is ignored.)
- Implicitly mirror the source code. Since one half of every valid Stack Cats program is redundant, there should be options to omit either everything in front of or after the centre character. As an example, consider the source code `:>[(!)-`. With one option, this would be implicitly mirrored to the right to give `:>[(!)-(!)]<:`, and with another it would be implicitly mirrored to the left to give `-(!)]<:>[(!)-`. Note that one character isn't mirrored, because that would result in a trivial even-length program.

## Commands

In the following section, "the stack" refers to the stack currently pointed at by the tape head, and "the top" refers to the top value on that stack.

### Control Flow

Remember that `()` and `{}` always have to be balanced correctly.

- `(`: If the top is zero or negative, control flow continues after the matching `)`.
- `)`: If the top is zero or negative, control flow continues after the matching `(`.
- `{`: Remembers the top.
- `}`: If the top differs from the value remembered at the matching `{`, control flow continues after the matching `{` (without remembering a new value).

In summary, `()` is a loop which is entered and left only when the top is positive, whereas `{}` is a loop which always iterates at least once and stops when the value from the beginning is seen again at the end of an iteration.

### Arithmetic

- `-`: Negate the top (i.e. multiply by `-1`).
- `!`: Take the bitwise NOT of the top (this is equivalent to incrementing and negating).
- `*`: Toggle the least-significant bit of the top. In other words, compute `x XOR 1`.
- `_`: Pop `a`, pop `b`, push `b`, push `b - a`.
- `^`: Pop `a`, pop `b`, push `b`, push `b XOR a`.

### Stack manipulation

- `:`: Swap the top two elements of the stack.
- `+`: Swap the top and third elements of the stack.
- `=`: Swap the top elements of the two adjacent stacks.
- `|`: Reverse all values on the stack down to (and excluding) the first zero from the top.
- `T`: If the top is non-zero, reverse the entire stack (down to and including the bottommost non-zero value).

### Movement and tape manipulation

- `<`: Move the tape head left one stack.
- `>`: Move the tape head right one stack.
- `[`: Move the tape head left one stack, taking the top with it.
- `]`: Move the tape head right one stack, taking the top with it.
- `I`: If the top is negative, do `[-`, if it is positive, do `]-`, if it is zero, do nothing.
- `/`: Swap the current stack with the stack to the left, and move the tape head left.
- `\`: Swap the current stack with the stack to the right, and move the tape head right.
- `X`: Swap the stacks left and right of the current stack.

## Interpreters

This repository contains two reference implementations, one in Python and one in Ruby.

### Python

*work in progress*

### Ruby

The Ruby interpreter can be run as follows:

    ruby ./interpreter.rb [options] ./program.sks

It supports the following options:

- `-i` use integer input.
- `-o` use integer output.
- `-n` use both integer input and output. (`n` for **n**umeric.)
- `-m` implicitly mirror the source code to the right.
- `-M` instead of executing the program, mirror it to the right and print it.
- `-l` and `-L`, same as `-m` and `-M` but mirror the program to the left.
- `-d` debug level 1: the command `"` can be inserted into the program to print debug information. All `"` are stripped before checking symmetry.
- `-D` debug level 2: print debug information after every command.

Options can be combined like `-imd`.
