"""Class examples"""

class Vehicle:
    def __init__(self, wheels, name):
        """The constructor"""
        self.wheels = wheels
        self.name = name
    def __len__(self):
        """Used with len(...) function"""
        return self.wheels
    def __repr__(self):
        """Resembles toString() method, used with str(...)"""
        return f"I'm a vehicle with {self.wheels} wheels!"
    def drive(self, x):
        """Normal instance method"""
        return f"Driving forward on my {self.wheels} wheels, {x} distance"
    def go(this, x):
        """Normal instance method, but uses this instead of self"""
        return f"Driving forward on my {this.wheels} wheels, {x} distance"

v = Vehicle(3, 'sammy') # instantiate vehicle

print(v) # uses __repr__
print(str(v)) # uses __str__ or __repr__
print(v.__repr__()) # same thing

print(len(v)) # uses __len__
print(v.__len__())

print(v.drive(10)) # call method
print(Vehicle.drive(v, 10)) # ALSO the same


"""Subclass Vehicle"""
class Car(Vehicle):
    NUM_WHEELS = 4 # Class variables
    def __init__(self, name):
        """Car calls the super constructor and it works the same"""
        super().__init__(Car.NUM_WHEELS, name)
    def drive(self, x):
        """Overrided the method! Not necessary. But I can do it."""
        return super().drive(x + 1)
    def bump(self):
        """A new instance method that calls a super method"""
        word = super().drive(-1)
        return word + f" Woops, I bumped you."
    def __len__(self):
        return 100
    
c = Car('ferrari')

isinstance(c, Car) # True
isinstance(c, Vehicle) # True
type(c) == Car # True
type(c) == Vehicle # False

c.drive(10) # nearly the same as parent
print(c) # uses Vehicle.__repr__ still
print(len(c)) # uses Car.__len__ now

