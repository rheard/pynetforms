from unittest import TestCase


class ExpandedTestCase(TestCase):
    def assertAllEqual(self, *args, msg=None):
        """Modify assertEqual to allow for multiple inputs."""
        for arg1, arg2 in zip(args, args[1:]):
            self.assertEqual(arg1, arg2, msg=msg)
