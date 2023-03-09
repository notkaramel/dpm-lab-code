from statistics import mean, stdev
from collections import Counter, defaultdict
import math


def square(x):
    return x*x


def vector_length(vector):
    return math.sqrt(sum(map(square, vector)))


def normalize(vector):
    n = vector_length(vector)
    return [x/n for x in vector]


def text_to_lists(text, row_length=3):
    return [tuple(map(int, line.strip().split(',')[:row_length]))
            for line in text.strip().split('\n')]

def circ_dist(angle1, angle2):
    '''
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
    '''
    return min((angle1-angle2)%360, (angle2-angle1)%360)

class RGBData:

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
    def from_text(text):
        return RGBData.from_samples(text_to_lists(text))

    @staticmethod
    def from_csv(filename):
        with open(filename, 'r') as f:
            return RGBData.from_text(f.read())

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

class ColorProfile:
    UNKNOWN = None
    _DATA_GEN_SIZE = 500

    @staticmethod
    def from_csv(filename, name, color_threshold=3, num_terms=3):
        with open(filename, 'r') as f:
            data = text_to_lists(f.read())
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
        self.color_mean = None if color_mean is None else RGBData.from_sample(color_mean)
        self.color_stdev = color_stdev
        self.color_threshold = color_threshold

        if color_mean is not None and color_stdev is not None:
            self.gen_func = [ColorProfile.gaussian_func(
                m, s) for m, s in zip(color_mean, color_stdev)]

        self.data = None

    def get_data(self):
        if self.data is None and self.gen_func is not None:
            # Generate the data based on the gaussian functions
            for i in range(self._DATA_GEN_SIZE):
                pass
        return self.data

    @staticmethod
    def gaussian_func(mean_val, stdev_val):
        a = mean_val
        s = stdev_val

        def func(x):
            term = - (x - a)**2 / (2 * s**2)
            pow = math.exp(term)
            # return pow
            return 1 / math.sqrt(2 * math.pi * s**2) * pow

        return func

    def __repr__(self):
        return f"Color[{self.name}]"


ColorProfile.UNKNOWN = ColorProfile("unknown")


class ColorGroup:
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
    doctest.testmod()
    profile_data = {
        'blue': normalize([0.4545, 0.6426, 0.6122]),
        'yellow': normalize([0.8432, 0.5208, 0.1325]),
        'orange': normalize([0.9501, 0.2868, 0.1158]),
        'red': normalize([0.9501, 0.0868, 0.0158]),
    }
    profiles = [ColorProfile(name, color_mean=RGBData.from_sample(dat), color_stdev=[.1, .1, .1],
                             color_threshold=1) for name, dat in profile_data.items()]

    detector = ColorDetector(
        profiles, ColorGroup.gaussian_dist, ColorDetector.by_min_with_threshold)
