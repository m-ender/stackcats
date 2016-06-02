# coding: utf-8

require_relative 'stack'

class Tape
    def initialize 
        @tape_right = [Stack.new]
        @tape_left = []
    end

    def peek
        @tape_right[0].peek
    end

    def push value
        @tape_right[0].push value
    end

    def pop
        @tape_right[0].pop
    end

    def empty?
        @tape_right[0].empty?
    end

    def move_left
        @tape_left << Stack.new if @tape_left.empty?
        @tape_right.unshift @tape_left.pop
        @tape_right.pop if @tape_right[-1].empty?
    end

    def move_right
        @tape_left.push @tape_right.shift
        @tape_left.shift if @tape_left[0].empty?
        @tape_right << Stack.new if @tape_right.empty?
    end

    def swap_left
        @tape_left << Stack.new if @tape_left.empty?
        @tape_left[-1], @tape_right[0] = @tape_right[0], @tape_left[-1]
        @tape_left.shift if @tape_left[0].empty?
    end

    def swap_right
        @tape_right << Stack.new if @tape_right.size < 2
        @tape_right[0], @tape_right[1] = @tape_right[1], @tape_right[0]
        @tape_right.pop if @tape_right[-1].empty?
    end
end