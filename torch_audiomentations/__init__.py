from .augmentations.gain import Gain
from .augmentations.peak_normalization import PeakNormalization
from .augmentations.polarity_inversion import PolarityInversion
from .augmentations.shift import Shift
from .core.composition import Compose
from .utils.config import from_dict, from_yaml
from .utils.convolution import convolve

__version__ = "0.4.0"
