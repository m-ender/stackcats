# coding: utf-8

require_relative 'stack'

class Tape
    def initialize 
        @pos = 0
        @tape = [Stack.new]
    end

    def stack
        @tape[@pos]
    end

    def peek
        stack.peek
    end

    def push value
        stack.push value
    end

    def pop
        stack.pop
    end

    def empty?
        stack.empty?
    end

    def reverse!
        stack.reverse!
    end

    def move_left
        if @pos == 0
            @tape.unshift Stack.new 
        else
            @pos -= 1
        end
        @tape.pop if @tape[-1].empty?
    end

    def move_right
        if @tape[0].empty?
            @tape.shift
        else
            @pos += 1
        end
        @tape << Stack.new if @pos == @tape.size
    end

    def swap_left
        if @pos == 0
            @tape.unshift Stack.new
            @pos += 1
        end
        @tape[@pos], @tape[@pos-1] = @tape[@pos-1], @tape[@pos]
        if @tape[0].empty?
            @tape_left.shift
            @pos -= 1
        end
    end

    def swap_right
        @tape << Stack.new if @pos == @tape.size-1
        @tape[@pos], @tape[@pos+1] = @tape[@pos+1], @tape[@pos]
        @tape_left.pop if @tape[-1].empty?
    end

    def to_s
        max_depth = @tape.map(&:depth).max
        widths = @tape.map do |st|
            (st.to_a.map{ |val| val.to_s.size } + [1]).max
        end
        tape_head = ' '*(3 + widths[0..@pos].reduce(:+) + @pos) + 'v'
        ([tape_head] + max_depth.times.map do |y|
            pos = max_depth - y - 1
            surroundings = pos == 0 ? '...' : '   '
            ([surroundings] + @tape.each_with_index.map do |st, i|
                list = st.to_a
                if pos < list.size
                    list[pos].to_s.rjust(widths[i])
                else
                    ' '*widths[i]
                end
            end + [surroundings]) * ' '
        end + ['    ' + widths.map{|w|'0'.rjust(w)} *' ', tape_head.tr('v','^')]) * $/ 
    end
end