from encoders import MultiEncoder, FixedWeightEncoder
import unittest
class TestMultiEncoder(unittest.TestCase):
    def test_multi_encoder_basic(self):
        # Create two fixed weight encoders
        encoder1 = FixedWeightEncoder(n=10, w=3, lower_bound=0, upper_bound=10)
        encoder2 = FixedWeightEncoder(n=8, w=2, lower_bound=0, upper_bound=10)
        # Create a MultiEncoder and add the two encoders
        multi_encoder = MultiEncoder(xmin=0, xmax=10)
        multi_encoder.add(encoder1)
        multi_encoder.add(encoder2)
        # Test encoding a value
