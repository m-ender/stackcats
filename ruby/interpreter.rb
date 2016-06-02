# coding: utf-8

require_relative 'stackcats'

debug_level = 0
mirror = false

while ARGV[0][0] == '-'
    case ARGV[0]
    when '-d'
        debug_level = 1
    when '-D'
        debug_level = 2
    when '-m'
        mirror = true
    else
        $stderr.puts "Unknown command-line option #{ARGV[0]}"
    end

    ARGV.shift
end

source = ARGF.read

source += source[0..-2].reverse.tr('(){}[]<>\/', ')(}{][></\\') if mirror

StackCats.run(source, debug_level)