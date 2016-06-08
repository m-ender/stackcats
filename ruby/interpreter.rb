#!/usr/bin/env ruby
# coding: utf-8

require_relative 'stackcats'

def mirror str
    str + str[0..-2].reverse.tr('(){}[]<>\/', ')(}{][></\\')
end

debug_level = 0
mirrored = false
print_mirrored = false
num_input = num_output = false

while ARGV[0][0] == '-'
    debug_level = 1 if ARGV[0][/d/]
    debug_level = 2 if ARGV[0][/D/]
    mirrored = true if ARGV[0][/m/]
    print_mirrored = true if ARGV[0][/M/]
    num_input = num_output = true if ARGV[0][/n/]
    num_input = true if ARGV[0][/i/]
    num_output = true if ARGV[0][/o/]

    ARGV.shift
end

source = ARGF.read

if print_mirrored
    puts mirror source
    exit
end

source = mirror source if mirrored

StackCats.run(source, num_input, num_output, debug_level)