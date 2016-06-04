# Stack Cats

**Stack Cats** (abbreviated as **SKS**) is a stack-based, [reversible](https://en.wikipedia.org/wiki/Reversible_computing) (esoteric) programming language. It was originally conceived of [for a language-design challenge on Code Golf Stack Exchange](http://codegolf.stackexchange.com/q/61804/8478), but later designed and developed independently of that.

## Basics

Every program in Stack Cats is written on a single line, where each character is a command. Being a reversible programming language means that for every command there is a way to undo it. The language is designed such that any snippet of commands can be undone by *mirroring* it. This means that the string of commands is reversed and all characters that come in symmetric pairs are swapped (`()`, `{}`, `[]`, `<>`, `\/`). For instance, the snippet `>[[(!-)/` undoes the snippet `\(-!)]]<`. Therefore, Stack Cats programs are made up exclusively of characters which are either self-symmetric (in most fonts) like `-_|!:I` or which come in pairs, i.e. `(){}[]<>\/`. Note that from a theoretical standpoint, self-symmetric characters compute [involutions](https://en.wikipedia.org/wiki/Involution_(mathematics)), while symmetric pairs compute [bijections](https://en.wikipedia.org/wiki/Bijection) (and their inverses).

## Syntax

There are only two syntactic rules for Stack Cats:

1. Every valid program must have mirror symmetry. That is, if the entire program is mirrored (see above), it must remain unchanged. This has a few implications. a) Every Stack Cats program computes an involution on the global memory state (since every program is its own inverse). b) Every even-length program computes the identity (i.e. a [cat program](http://esolangs.org/wiki/Cat_program)) provided that it terminates, since the second half undoes the first. c) Every non-trivial program has odd length. If we call the command in the centre of the program `A`, then every such program has the structure `pAq`, where `p` is an arbitrary program and `q` computes its inverse. Note that `A` needs to be one of the self-symmetric characters, so it is itself an involution. Hence, programming in Stack Cats is about finding a function `p` which transforms a very simple involution `A` into the desired program.
2. Parentheses, `()`, and braces, `{}`, need to be balanced correctly, as they form loops. (`[]` and `<>` can appear individually and don't need be matched.)

## Memory model

Stack Cats operates on an infinite tape of stacks. The tape has a tape head which can be moved and points at the "current" stack. Commands tend to operate locally on or near the tape head. The stacks store arbitrary-precision (signed) integers and contain an implicit, infinite amount of zeros at the bottom. Initially, all stacks but the one where the tape head starts are empty (apart from those zeros).

## I/O

To ensure full reversibility, Stack Cats has no I/O commands, as these side-effects cannot be reversed cleanly. Instead, when the program starts, all input (which has to be finite) is read from the standard input stream. All the bytes are pushed onto the initial stack, with the first input byte on top and the last input byte at the bottom.

At the end of the program (provided it terminates), the contents of the current stack (pointed at by the tape head) are taken modulo 256 and printed as bytes to the standard output stream. Again, the value on top is used for the first byte and the value at the bottom is used for the last byte. Note that to print trailing null-bytes, you should use a multiple of 256 (other than zero), because all zeros at the bottom are assumed to be part of the implicit infinite pool of zeros and will not be printed.

## Commands

*tbd*