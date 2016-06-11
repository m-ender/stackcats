#!/usr/bin/env ruby
# coding: utf-8

require_relative 'stackcats'

def mirror_right str
    str + str[0..-2].reverse.tr('(){}[]<>\\\\/', ')(}{][></\\\\')
end

def mirror_left str
    str[1..-1].reverse.tr('(){}[]<>\\\\/', ')(}{][></\\\\') + str
end

debug_level = 0
mirrored = false
print_mirrored = false
mirror_r = true
num_input = num_output = false

ARGV.select!{|arg|
    if arg[0] == '-'
        debug_level = 1 if arg[/d/]
        debug_level = 2 if arg[/D/]
        mirrored = true if arg[/m|l/]
        print_mirrored = true if arg[/M|L/]
        mirror_r = false if arg[/l/i]
        num_input = num_output = true if arg[/n/]
        num_input = true if arg[/i/]
        num_output = true if arg[/o/]

        false
    else
        true
    end
}

source = ARGF.readline.chomp

if print_mirrored
    puts (mirror_r ? mirror_right(source) : mirror_left(source))
    exit
end

if mirrored
    source = mirror_r ? mirror_right(source) : mirror_left(source)
end

begin
    StackCats.run(source, num_input, num_output, debug_level)
rescue => e
    $stderr.puts e.message
end