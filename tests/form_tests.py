import netforms

from .utils import ExpandedTestCase


class TestPythonNames(ExpandedTestCase):
    """Basic tests to ensure that we can correctly interface between C# and Python names and types."""

    def test_setting_csharp_attr(self):
        """Test that we can set a C# attribute, and that the Python attribute reflects the change"""
        form = netforms.forms.Form()
        form.Text = "Testing"
        self.assertAllEqual(form.text, form.Text, "Testing")

    def test_setting_python_attr(self):
        """Test that we can set a Python attribute, and that the C# attribute reflects the change"""
        form = netforms.forms.Form()
        form.text = "Testing"
        self.assertAllEqual(form.text, form.Text, "Testing")

    def test_setting_attr_in_init(self):
        """Test that we can use a Python attribute in the __init__"""
        form = netforms.forms.Form(text="Testing")
        self.assertAllEqual(form.text, form.Text, "Testing")

    def test_implicit_attr_value_type_conversion(self):
        """Test that we can set an attribute using a Python type and have it converted on the fly"""
        form = netforms.forms.Form(text=0)
        self.assertEqual(form.text, "0")
