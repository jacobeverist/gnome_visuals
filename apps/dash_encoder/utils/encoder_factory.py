import sys
import os

# Add parent directory to path to import gnomecode
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from gnomecode.encoders import PeriodicScalarEncoder, PeriodicCellEncoder, MultiEncoder
except ImportError:
    print("Warning: Could not import gnomecode encoders. Using mock implementations.")

    class MockEncoder:
        def __init__(self, n=8, w=3, xmin=-1.0, xmax=2.0):
            self.n = n
            self.w = w
            self.xmin = xmin
            self.xmax = xmax
            self.region_boundaries = list(np.linspace(xmin, xmax, n+1))
            self.region_centers = list(np.linspace(xmin + (xmax-xmin)/(2*n),
                                                  xmax - (xmax-xmin)/(2*n), n))

        def encode(self, x):
            import numpy as np
            # Simple mock encoding
            if not isinstance(x, (list, np.ndarray)):
                x = [x]
            result = []
            for val in x:
                encoded = np.zeros(self.n)
                if self.xmin <= val <= self.xmax:
                    # Simple binning
                    bin_idx = int((val - self.xmin) / (self.xmax - self.xmin) * self.n)
                    bin_idx = max(0, min(self.n - 1, bin_idx))
                    # Set w consecutive bits
                    for i in range(self.w):
                        if bin_idx + i < self.n:
                            encoded[bin_idx + i] = 1
                result.append(encoded)
            return result[0] if len(result) == 1 else np.array(result)

    PeriodicScalarEncoder = MockEncoder
    PeriodicCellEncoder = MockEncoder
    MultiEncoder = MockEncoder

import numpy as np

def create_encoder_from_params(params):
    """Create an encoder instance from parameter dictionary."""

    encoder_type = params.get('encoder_type', 'periodic_scalar')
    n = params.get('n', 8)
    w = params.get('w', 3)
    period = params.get('period', 1.0)
    offset = params.get('offset', 0.0)
    xmin = params.get('xmin', -1.0)
    xmax = params.get('xmax', 2.0)

    try:
        if encoder_type == 'periodic_scalar':
            if hasattr(PeriodicScalarEncoder, '__init__'):
                # Try to use real PeriodicScalarEncoder
                encoder = PeriodicScalarEncoder(
                    n=n,
                    w=w,
                    period=period,
                    lower_bound=xmin + offset,
                    upper_bound=xmax + offset
                )
            else:
                # Use mock encoder
                encoder = PeriodicScalarEncoder(n=n, w=w, xmin=xmin, xmax=xmax)

        elif encoder_type == 'periodic_cell':
            if hasattr(PeriodicCellEncoder, '__init__'):
                # Try to use real PeriodicCellEncoder
                encoder = PeriodicCellEncoder(
                    n=n,
                    period=period,
                    l_frac=w/n  # Convert w to length fraction
                )
            else:
                # Use mock encoder
                encoder = PeriodicCellEncoder(n=n, w=w, xmin=xmin, xmax=xmax)

        elif encoder_type == 'multi_encoder':
            # Create a MultiEncoder with multiple sub-encoders
            multi_encoder = MultiEncoder(xmin=xmin, xmax=xmax)

            # Add a few different periodic encoders
            for i, scale in enumerate([0.5, 1.0, 1.5]):
                try:
                    sub_encoder = PeriodicScalarEncoder(
                        n=n,
                        w=w,
                        period=period * scale,
                        lower_bound=xmin + offset,
                        upper_bound=xmax + offset
                    )
                    multi_encoder.add_encoder(sub_encoder)
                except:
                    # Use mock if real encoder fails
                    sub_encoder = PeriodicScalarEncoder(n=n, w=w, xmin=xmin, xmax=xmax)
                    multi_encoder.add_encoder(sub_encoder)

            encoder = multi_encoder
        else:
            # Default to periodic scalar
            encoder = PeriodicScalarEncoder(n=n, w=w, xmin=xmin, xmax=xmax)

        return encoder

    except Exception as e:
        print(f"Error creating encoder: {e}")
        # Fallback to mock encoder
        return MockEncoder(n=n, w=w, xmin=xmin, xmax=xmax)

def get_encoder_info(encoder):
    """Extract information from an encoder for display."""

    info = {
        'type': type(encoder).__name__,
        'n_bins': getattr(encoder, 'n', 'Unknown'),
        'width': getattr(encoder, 'w', 'Unknown'),
        'boundaries': getattr(encoder, 'region_boundaries', []),
        'centers': getattr(encoder, 'region_centers', [])
    }

    return info