# coding: utf-8

require_relative 'stack'
require_relative 'tape'

class StackCats

    class ProgramError < Exception; end

    OPERATORS = {
        # Asymmetric characters:
        # "#$%&,12345679;?@`~"
        # Unused self-symmetric characters:
        # " '*+.=08AMOUVWXYovwx"
        # Unused symmetric pairs:
        # "bdpq"

        # Symmetric pairs (these need to be each other's inverse):
        '('  => :open_sign_loop,
        ')'  => :close_sign_loop,
        '/'  => :swap_left,
        '\\' => :swap_right,
        '<'  => :move_left,
        '>'  => :move_right,
        '['  => :push_left,
        ']'  => :push_right,
        '{'  => :open_value_loop,
        '}'  => :close_value_loop,

        # Self-symmetric characters:
        '!'  => :bit_not,
        '"'  => :debug,
        '-'  => :negate,
        ':'  => :swap,
        'I'  => :cond_push,
        'T'  => :cond_neg,
        '^'  => :xor,
        '_'  => :sub,
        '|'  => :reverse,
    }

    OPERATORS.default = :invalid

    def self.run(src, debug_level=0, in_str=$stdin, out_str=$stdout, max_ticks=-1)
        new(src, debug_level, in_str, out_str, max_ticks).run
    end

    def initialize(src, debug_level=false, in_str=$stdin, out_str=$stdout, max_ticks=-1)
        @debug_level = debug_level
        @in_str = in_str
        @out_str = out_str
        @max_ticks = max_ticks

        @program = src

        preprocess_source

        @ip = 0
        @loop_conds = Stack.new

        @tape = Tape.new

        @tick = 0
    end

    def preprocess_source
        # Validate symmetry
        program = @debug_level > 0 ? @program.gsub('"', '') : @program
        if program != program.reverse.tr('(){}[]<>\/', ')(}{][></\\')
            $stderr.puts "Error: program is not symmetric"
            exit
        end

        # Pre-parse loops
        @loop_targets = Hash.new
        open_loops = Stack.new

        pos = 0
        @program.each_char do |c|
            op = OPERATORS[c]
            if op == :invalid || op == :debug && @debug_level == 0
                $stderr.puts "Error: invalid character in source code, #{c}"
                exit
            end

            case op
            when :open_value_loop, :open_sign_loop
                open_loops.push [op, pos]
            when :close_value_loop
                if open_loops.empty? || open_loops.peek[0] != :open_value_loop
                    $stderr.puts "Error: unmatched }"
                    exit
                end
                _, open_pos = open_loops.pop
                @loop_targets[pos] = open_pos
            when :close_sign_loop
                if open_loops.empty? || open_loops.peek[0] != :open_sign_loop
                    $stderr.puts "Error: unmatched )"
                    exit
                end
                _, open_pos = open_loops.pop
                @loop_targets[open_pos] = pos
                @loop_targets[pos] = open_pos
            end

            pos += 1
        end

        if !open_loops.empty?
            case open_loops.peek[0]
            when :open_value_loop
                $stderr.puts "Error: unmatched {"
                exit
            when :open_sign_loop
                $stderr.puts "Error: unmatched ("
                exit
            end
        end
    end

    def run
        input = []
        while (val = read_byte)
            input << val.ord
        end

        input.reverse.each do |val|
            @tape.push val
        end
        while @ip < @program.size
            print_debug_info if @debug_level > 1
            
            op = @program[@ip]
            process op
            @ip += 1

            @tick += 1
            break if @max_ticks > -1 && @tick >= @max_ticks
        end

        print_debug_info if @debug_level > 1

        until @tape.empty?
            @out_str.print (@tape.pop % 256).chr
        end

        @max_ticks > -1 && @tick >= @max_ticks
    end

    private

    def print_debug_info
        $stderr.puts "\nTick #{@tick}"
        $stderr.puts "Tape:"
        $stderr.puts @tape.to_s
        $stderr.puts "Program:"
        $stderr.puts @program
        $stderr.puts ' '*@ip + '^'
    end

    def process op
        case OPERATORS[op]
        # Symmetric pairs
        when :open_sign_loop
            @ip = @loop_targets[@ip] if @tape.peek < 1
        when :close_sign_loop
            @ip = @loop_targets[@ip] if @tape.peek < 1
        when :swap_left
            @tape.swap_left
            @tape.move_left
        when :swap_right
            @tape.swap_right
            @tape.move_right
        when :move_left
            @tape.move_left
        when :move_right
            @tape.move_right
        when :push_left
            val = @tape.pop
            @tape.move_left
            @tape.push val
        when :push_right
            val = @tape.pop
            @tape.move_right
            @tape.push val
        when :open_value_loop
            @loop_conds.push @tape.peek
        when :close_value_loop
            if @tape.peek == @loop_conds.peek
                @loop_conds.pop
            else
                @ip = @loop_targets[@ip]
            end

        # Self-symmetric characters
        # Arithmetic
        when :bit_not
            @tape.push ~@tape.pop
        when :negate
            @tape.push -@tape.pop
        when :xor
            val = @tape.pop
            @tape.push (@tape.peek ^ val)
        when :sub
            val = @tape.pop
            @tape.push (@tape.peek - val)

        when :swap
            top, bottom = @tape.pop, @tape.pop
            @tape.push top
            @tape.push bottom
        when :reverse
            list = []
            while @tape.peek != 0
                list << @tape.pop
            end

            list.each { |val| @tape.push val }

        when :cond_push
            val = @tape.pop
            if val < 0
                @tape.move_left
            elsif val > 0
                @tape.move_right
            end
            @tape.push val
        when :cond_neg
            val = @tape.pop
            @tape.push -@tape.pop if val > 0
            @tape.push val

        when :debug
            print_debug_info
        end
    end

    def read_byte
        result = nil
        if @next_byte
            result = @next_byte
            @next_byte = nil
        else
            result = @in_str.read(1)
            # result = @in_str.read(1) while result =~ /\r|\n/
        end
        result
    end
end