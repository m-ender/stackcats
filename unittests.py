import io
import sys
import unittest

from stackcats import StackCats, InvalidCodeException

class TestStackCats(unittest.TestCase):
    def setUp(self):
        sys.stdout = io.StringIO()

    def test_palindromic(self):
        for code in ["((--((", "(----", ">->"]:
            with self.assertRaises(InvalidCodeException):
                self.run_test(code)

        for code in ["((!!))", "(-!-)", "<->"]:
            self.run_test(code)

    def test_increment(self):
        self.run_test("-!"*97 + "-", "a")

    def test_swap(self):
        self.run_test((":", "abcde"), "bacde")

    def test_xor(self):
        self.run_test(("^", "Abcde"), "#bcde")

    def run_test(self, prog, output=None):
        if isinstance(prog, tuple):
            prog, input_ = prog
        else:
            input_ = ""

        sc = StackCats(prog)
        sc.run(input_)

        if output is not None:
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
