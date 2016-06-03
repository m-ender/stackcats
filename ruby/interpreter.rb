# coding: utf-8

require_relative 'stackcats'

def mirror str
    str + str[0..-2].reverse.tr('(){}[]<>\/', ')(}{][></\\')
end

debug_level = 0
mirrored = false
print_mirrored = false

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

StackCats.run(source, debug_level)