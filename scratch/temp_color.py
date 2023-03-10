from statistics import mean, stdev
from collections import Counter, defaultdict
import math
import random


def square(x):
    """Returns x to the power of 2"""
    return x*x


def vector_length(vector):
    """Takes a vector of any size and gives the length of the vector"""
    return math.sqrt(sum(map(square, vector)))


def normalize(vector):
    """Takes a vector of any size and turns it into a unit vector"""
    n = vector_length(vector)
    return [x/n for x in vector]


def text_to_lists(text, row_length=3, row_range=None):
    """Convert text to a 2D list

    Inner lists are separated by newlines, and elements
    of an inner list are separated by commas.

    >>> ls = [(1,2,3), (3,4,5), (4,5,6)]
    >>> conv = (lambda x : '\\n'.join([ ','.join(map(str, row)) for row in x ]))
    >>> text_to_lists(conv(ls)) == ls
    True
    >>> text_to_lists(conv(ls[:2]), row_range=range(2)) == ls[:2]
    True
    >>> text_to_lists(conv(ls[1:3]), row_range=range(1,3)) == ls[1:3]
    True
    >>> text_to_lists(conv(ls[0:5:2]), row_range=range(0,5,2)) == ls[0:5:2]
    True
    """
    list_text = text.strip().split('\n')
    if row_range is not None and isinstance(row_range, range):
        list_text = list_text[row_range.start: row_range.stop: row_range.step]

    return [tuple(map(int, line.strip().split(',')[:row_length]))
            for line in list_text]


def circ_dist(angle1, angle2):
    """Returns the closest between to angles on a circle.
    Works in degrees, not radians.

    Example: the closest distance between 5 and 355 deg is 10 deg, not 350

    >>> circ_dist(60, 300)
    120
    >>> circ_dist(300, 60)
    120
    >>> circ_dist(0, 180)
    180
    >>> circ_dist(5, 355)
    10
    >>> circ_dist(120, 240)
    120
    """
    return min((angle1-angle2) % 360, (angle2-angle1) % 360)


class RGBData:
    """A way to store an RGB data and easily convert it to different formats

    Initialization:
    RGBData(50, 100, 20) # In order of R, G, and B color channels
    RGBData.from_sample([50, 100, 20])
    RGBData.poll(color_sensor) # color_sensor needs a .get_rgb() function

    RGBData.from_samples([[50, 100, 20], [50, 100, 30]]) # List of RGBData objects
    RGBData.from_text('50,100,20\n30,40,10') # List of RGBData objects
    RGBData.from_csv('some_file.csv') # Each row is a comma-separated list of 3 values ideally

    Usage:
    r, g, b = 3, 4, 5
    dat = RGBData(r, g, b)

    dat.brightness => vector_length of <r, g, b>
    dat.normalized => unit vector version of <r, g, b>
    dat.hsv        => HSV version
    dat.r, dat.g, dat.b => access each original color channel
    list(dat)      => gives [r, g, b]

    print(dat)     => prints "RGB[r, g, b]"

    """

    UNKNOWN = None

    @staticmethod
    def poll(sensor):
        if hasattr(sensor, 'get_rgb'):
            return RGBData.from_sample(sensor.get_rgb())
        else:
            raise RuntimeError("Given sensor is not a valid Color Sensor")

    @staticmethod
    def from_sample(rgb_sample):
        return RGBData(*[v for v in rgb_sample][:3])

    @staticmethod
    def from_samples(rgb_samples):
        return [RGBData.from_sample(sample) for sample in rgb_samples]

    @staticmethod
    def from_text(text, row_length=3, row_range=None):
        return RGBData.from_samples(text_to_lists(text, row_length=row_length, row_range=row_range))

    @staticmethod
    def from_csv(filename, num_terms=3, row_range=None):
        with open(filename, 'r') as f:
            return RGBData.from_text(f.read(), row_length=num_terms, row_range=row_range)

    def __init__(self, r, g, b):
        self._r = r
        self._g = g
        self._b = b
        self._dat = (r, g, b)

    def __iter__(self):
        return iter(self._dat)

    @property
    def brightness(self):
        return self.length

    @property
    def length(self):
        if not hasattr(self, '_length'):
            self._length = vector_length(self._dat)
        return self._length

    @property
    def normalized(self):
        if not hasattr(self, '_normal'):
            n = self.length
            if n == 0:
                self._normal = (0, 0, 0)
            else:
                self._normal = (self.r/n, self.g/n, self.b/n)
        return self._normal

    @property
    def hsv(self):
        if not hasattr(self, '_hsv'):
            norm = self.normalized
            cmax = max(norm)
            cmin = min(norm)
            delt = cmax-cmin

            if delt == 0:
                h = 0
            elif cmax == norm[0]:
                h = 60 * ((norm[1] - norm[2])/delt % 6)
            elif cmax == norm[1]:
                h = 60 * ((norm[2] - norm[0])/delt + 2)
            elif cmax == norm[2]:
                h = 60 * ((norm[0] - norm[1])/delt + 4)

            self._hsv = (
                h,
                0 if cmax == 0 else delt/cmax,
                cmax
            )
        return self._hsv

    @property
    def r(self):
        return self._r

    @property
    def g(self):
        return self._g

    @property
    def b(self):
        return self._b

    def __repr__(self):
        return f'RGB[{round(self.r, 2)}, {round(self.g, 2)}, {round(self.b, 2)}]'

RGBData.UNKNOWN = RGBData(0, 0, 0)

class ColorProfile:
    """A method of storing the profile of a color as the mean and 
    standard deviation of its color channels.


    # name, rgb means, rgb stdev, and the 'minimum threshold' used for some processing functions
    profile = ColorProfile('red', [5, 6, 7], [0.1, 0.1, 0.1], 4)

    # name, raw collected data, 'minimum threshold' again
    profile = ColorProfile.from_data('red', [[1,2,3], [2,3,4]], 4)

    # Loading data from a CSV
    # filename, name, minimum threshold, 'num_terms' set to 3 for 3 rgb channels
    # (there is little reason to change 'num_terms' as it is the num of columns from the csv)
    profile = ColorProfile.from_csv('data.csv', 'red', 4, 3)


    # Randomly generates fake data based on means and stdevs
    # Can be useful if data does not exist, but means and stdevs do
    profile.generate_data() # Default: 500 iterations
    profile.generate_data(100)
    """

    UNKNOWN = None
    _DATA_GEN_SIZE = 500

    @staticmethod
    def from_csv(filename, name, color_threshold=3, num_terms=3, row_range=None):
        with open(filename, 'r') as f:
            data = text_to_lists(
                f.read(), row_length=num_terms, row_range=row_range)
            return ColorProfile.from_data(name, data, color_threshold)

    @staticmethod
    def from_data(name, data, color_threshold=3):
        # Generate mean and stdev from 2D Lists
        normal_data_t = list(zip(*map(normalize, data)))
        color_mean = list(map(mean, normal_data_t))
        color_stdev = list(map(stdev, normal_data_t))
        p = ColorProfile(name, color_mean, color_stdev, color_threshold)
        p.data = data
        return p

    def __init__(self, name, color_mean=None, color_stdev=None, color_threshold=3):
        self.name = name
        self.color_mean = RGBData.UNKNOWN if color_mean is None else RGBData.from_sample(
            color_mean)
        self.color_stdev = color_stdev
        self.color_threshold = color_threshold

        if color_mean is not None and color_stdev is not None:
            self.gen_func = [ColorProfile.gaussian_func(
                m, s) for m, s in zip(color_mean, color_stdev)]

        self.data = None

    def generate_data(self, iterations=500):
        """Randomly generates a 2D list of RGB values based on the current mean and stdev for each RGB colors.
        
        Imperfect, but potentially useful if random data is needed for some for of statistics/testing.
        """
        return [
            [random.gauss(m, s) for m, s in zip(self.color_mean.normalized, self.color_stdev)] for i in range(500)
        ]

    @staticmethod
    def gaussian_func(mean_val, stdev_val):
        """Creates a 1D Gaussian Distribution Function
        Area underneath the curve adds up to ~100

        func1 = ColorProfile.gaussian_func(0.4, 0.2) # mean and stdev

        func1(0.4) # gives the highest probability of an x-value
        """
        a = mean_val
        s = stdev_val

        def func(x):
            term = - (x - a)**2 / (2 * s**2)
            pow = math.exp(term)
            return 1 / math.sqrt(2 * math.pi * s**2) * pow

        return func

    def __repr__(self):
        return f"Color[{self.name}]"


ColorProfile.UNKNOWN = ColorProfile("unknown")


class ColorGroup:
    """An object to group together ColorProfile objects and 
    apply processing functions to them.

    """

    def __init__(self, profiles=None):
        if profiles is not None:
            self.profiles = [profile for profile in list(
                profiles) if isinstance(profile, ColorProfile)]
        else:
            self.profiles = []

    def append(self, profile):
        self.profiles.append(profile)

    def apply(self, func, color_sample):
        """Use a processing function func on the given color_sample vector, against all the stored color profiles.

        func is the type function(ColorProfile, List[float]) -> Any
        color_sample is the type List[float]
        """
        return {profile: func(profile, color_sample) for profile in self.profiles}

    @staticmethod
    def gaussian_dist(profile: ColorProfile, color_sample):
        color_sample = normalize(color_sample)
        return vector_length([abs(c-m)/s for c, m, s in zip(color_sample, profile.color_mean.normalized, profile.color_stdev)])

    @staticmethod
    def raw_dist(profile: ColorProfile, color_sample):
        color_sample = normalize(color_sample)
        return vector_length([abs(c-m) for c, m in zip(color_sample, profile.color_mean.normalized)])

    @staticmethod
    def hsv_dist(profile: ColorProfile, color_sample):
        """Gives an altered version of HSV.
        H => distance from profile.hsv to color_sample.hsv
        S => distance from profile.hsv to color_sample.hsv
        V/B => actual brightness of color_sample from vector length
        """
        dat = RGBData.from_sample(color_sample)
        h1, s1, v1 = dat.hsv
        h2, s2, v2 = profile.color_mean.hsv
        return circ_dist(h1, h2), abs(s2-s1), dat.brightness

    def __repr__(self):
        return f"Group[{','.join([ p.name for p in self.profiles])}]"


class ColorDetector:
    """ColorDetector uses a group ColorProfiles and preset functions to identify new color samples.

    Requires specification of:
    - a processor function to compare the new sample to each existing profile 
        (outputs some value per profile)
    - a detector function to choose one of the profiles 
        (based on the comparison result)

    Examples:

    # Euclidean distance between normalized RGB profile and RGB sample. Chooses color with shortest distance detected.
    detect0 = ColorDetector(profiles, ColorGroup.raw_dist, ColorDetector.by_min_value)

    # Every distance comparison is in units of standard deviations. Chooses color with shortest distance.
    # Gives unknown if sample is too far away from any one profile (uses minimum_threshold on profiles)
    detect1 = ColorDetector(profiles, ColorGroup.gaussian_dist, ColorDetector.by_min_with_threshold)

    # Uses HSV to compute distances (H, S, V) where H is the degrees distance from the profile.
    # Takes the shortest distance found.
    detect2 = ColorDetector(profiles, ColorGroup.hsv_dist, ColorDetector.by_min_value)
    """

    def __init__(self, profiles, processor_func, detector_func):
        self.color_group = ColorGroup(profiles)
        self.processor_func = processor_func
        self.detector_func = detector_func

    def determine(self, sample):
        data = self.color_group.apply(self.processor_func, sample)
        return self.detector_func(data)

    @staticmethod
    def by_min_value(data_dict: dict):
        final_profile = None
        final_value = None
        for profile, value in data_dict.items():
            if final_value is None or final_value > value:
                final_value = value
                final_profile = profile

        return final_profile, final_value

    @staticmethod
    def by_min_with_threshold(data_dict: dict):
        final_profile, final_value = ColorDetector.by_min_value(data_dict)

        if final_value <= final_profile.color_threshold:
            return final_profile, final_value
        else:
            return ColorProfile.UNKNOWN, final_value

    def __repr__(self):
        return f"Detector[{self.processor_func.__qualname__},{self.detector_func.__qualname__}]"


if __name__ == '__main__':
    import doctest
    # doctest.testmod()
    profile_data = {
        'blue': normalize([50, 50, 75]),
        'yellow': normalize([292, 212, 36]),
        'orange': normalize([284, 66, 27]),
        'red': normalize([245, 50, 28]),
    }
    profiles = [ColorProfile(name, color_mean=RGBData.from_sample(dat), color_stdev=[.1, .1, .1],
                             color_threshold=1) for name, dat in profile_data.items()]

    detector = ColorDetector(
        profiles, ColorGroup.gaussian_dist, ColorDetector.by_min_with_threshold)
