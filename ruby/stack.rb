# coding: utf-8

class Stack
    def initialize
        @stack = []
    end

    def depth
        @stack.size
    end

    def empty?
        @stack.empty?
    end

    def push value
        @stack << value unless empty? && value == 0
    end

    def pop
        empty? ? 0 : @stack.pop
    end

    def peek
        empty? ? 0 : @stack[-1]
    end

    def to_a
        @stack
    end

    def reverse!
        @stack.reverse!
    end
end