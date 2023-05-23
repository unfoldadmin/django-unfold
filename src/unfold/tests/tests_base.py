from unittest import TestCase


class DummyTestCase(TestCase):
    def test_dummy(self):
        self.assertEqual(1, 1)
