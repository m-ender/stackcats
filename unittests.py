import io
import sys
import unittest

from stackcats import StackCats, InvalidCodeException

class TestStackCats(unittest.TestCase):
    def setUp(self):
        sys.stdout = io.StringIO()

    def test_palindromic(self):
        for code in ["((;;((", "(;:;;", ">:>"]:
            with self.assertRaises(InvalidCodeException):
                self.run_test(code)

        for code in ["((;;))", "(;:;)", "<:>"]:
            self.run_test(code)

    def test_input(self):
        self.run_test(("1", "\n"), "e")

    def test_first_byte(self):
        code = "[r;r]"
        
        self.run_test((code, "abcde"), "a")
        self.run_test((code, "123456"), "1")
        self.run_test((code, "ABCDEFGHI"), "A")

    def test_last_byte(self):
        code = "r1;1r"
        
        self.run_test((code, "abcde"), "e")
        self.run_test((code, "123456"), "6")
        self.run_test((code, "ABCDEFGHI"), "I")

    def test_HW(self):
        self.run_test("<13>>33>100>108>114>111>87>32>44>111>108>108>101>72<<<<<<<<<<<<<r<;"
                      ">r>>>>>>>>>>>>>27<101<801<801<111<44<23<78<111<411<801<001<33<<31>",
                      "Hello, World!")

    def test_drop_first_n(self):
        code = "]]#[>[[<r<;>r>]]<]#[[" # n = 2

        self.run_test((code, "abcde"), "cde")
        self.run_test((code, "123456"), "3456")
        self.run_test((code, "ABCDEFGHI"), "CDEFGHI")
        
        code = "]]]#[>[[[<r<;>r>]]]<]#[[[" # n = 3

        self.run_test((code, "abcde"), "de")
        self.run_test((code, "123456"), "456")
        self.run_test((code, "ABCDEFGHI"), "DEFGHI")

    def test_copy_nth(self):
        code = "]]:[>[[<<]>:<[>>]]<]:[[" # n = 2

        self.run_test((code, "abcde"), "cabcde")
        self.run_test((code, "123456"), "3123456")
        self.run_test((code, "ABCDEFGHI"), "CABCDEFGHI")
        
        code = "]]]:[>[[[<<]>:<[>>]]]<]:[[[" # n = 3

        self.run_test((code, "abcde"), "dabcde")
        self.run_test((code, "123456"), "4123456")
        self.run_test((code, "ABCDEFGHI"), "DABCDEFGHI")

    def test_loop_addition(self):
        code = "<5{(>)<};{>(<)}5>" # n = 5
        for c in " 0aA": self.run_test((code, c), chr(ord(c) + 5))

        code = "<27{(>)<};{>(<)}72>" # n = 27
        for c in " 0aA": self.run_test((code, c), chr(ord(c) + 27))


    def run_test(self, prog, output=""):
        if isinstance(prog, tuple):
            prog, input_ = prog
        else:
            input_ = ""

        sc = StackCats(prog)
        sc.run(input_)
        self.assertEqual(self.output(), output)

        # Assert cat without middle
        if len(prog) % 2 == 1:
            prog = prog[:len(prog)//2] + prog[len(prog)//2 + 1:]

            sc = StackCats(prog)
            sc.run(input_)
            self.assertEqual(self.output(), input_)

    def output(self):
        val = sys.stdout.getvalue()
        sys.stdout = io.StringIO()
        return val

if __name__ == '__main__':
    unittest.main()
