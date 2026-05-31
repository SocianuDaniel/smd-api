"""example af a test"""

from django.test import SimpleTestCase
from . import calc


class CalcTests(SimpleTestCase):
    """Class tor testing """

    def test_numbers_add(self):
        res = calc.add_numbers(5, 6)
        self.assertEqual(res, 11)

    def test_subtract_nnumbers(self):
        """Test substraction of two numbers"""
        res = calc.substract(10, 15)

        self.assertEqual(res, 5)
