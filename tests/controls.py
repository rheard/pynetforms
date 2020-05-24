from clr import System

from netforms.controls import Button
from netforms.utils import Point

from .utils import ExpandedTestCase


class TestPythonNames(ExpandedTestCase):
    def test_python_names(self):
        button = Button()
        self.assertEqual(button.text, button.Text)

        button.Text = "Testing"
        self.assertAllEqual(button.text, button.Text, "Testing")

        button.text = "Testing2"
        self.assertAllEqual(button.text, button.Text, "Testing2")

    def test_python_names_in_init(self):
        button = Button(Text="Testing")
        self.assertAllEqual(button.Text, button.text, "Testing")

        button = Button(text="Testing")
        self.assertAllEqual(button.Text, button.text, "Testing")

    def test_get_value_type_conversion(self):
        button = Button()
        self.assertIsInstance(button.Location, tuple)
        self.assertIsInstance(button.location, tuple)

    def test_csharp_types_no_conversion(self):
        button = Button()

        button.location = System.Drawing.Point(12, 12)
        self.assertAllEqual(button.location, button.Location, (12, 12))

        button.Location = System.Drawing.Point(0, 0)
        self.assertAllEqual(button.location, button.Location, (12, 12))

    def test_implicit_type_conversion(self):
        button = Button()
        button.text = 0
        self.assertEqual(button.text, "0")

        # First two test native python types against csharp and python names.
        button.location = (12, 0)
        self.assertAllEqual(button.location, button.Location, (12, 0))

        button.Location = (0, 12)
        self.assertAllEqual(button.location, button.Location, (0, 12))

        # Test the dedicated Python types.
        button.location = Point(12, 12)
        self.assertAllEqual(button.location, button.Location, (12, 12))

        button.Location = Point(0, 0)
        self.assertAllEqual(button.location, button.Location, (12, 12))
