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
    case ARGV[0]
    when '-d'
        debug_level = 1
    when '-D'
        debug_level = 2
    when '-m'
        mirrored = true
    when '-M'
        print_mirrored = true
    when '-n'
        num_input = num_output = true
    when '-i'
        num_input = true
    when '-o'
        num_output = true
    else
        $stderr.puts "Unknown command-line option #{ARGV[0]}"
    end

    ARGV.shift
end

source = ARGF.read

if print_mirrored
    puts mirror source
    exit
end

source = mirror source if mirrored

StackCats.run(source, num_input, num_output, debug_level)