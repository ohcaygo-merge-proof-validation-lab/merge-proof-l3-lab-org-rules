import unittest
from l3_coverage_fixture import bounded_score

class CoverageFixtureTest(unittest.TestCase):
    def test_lower_boundary(self):
        self.assertEqual(bounded_score(-1), 0)
    def test_upper_boundary(self):
        self.assertEqual(bounded_score(101), 100)
    def test_interior(self):
        self.assertEqual(bounded_score(42), 42)

if __name__ == '__main__':
    unittest.main()
