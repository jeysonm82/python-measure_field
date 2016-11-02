# Measure Field
Use it to represent and  manipulate measures in python.

## Example

```python
from measure_field import Measure, Unit

t1 = Measure(cm=1)

print t1.mm # Convert to mm

t2 = Measure(mm=20)

print t1 + t2 # Prints 3 cm

print t1 * t2 # Prints 2 cm^2

print t1 / t2 # Prints 0.5


t2 = Measure(s=2)
print t1 / t2 # Prints 0.5 cm / s
```

# Author

Jeyson Molina <jeyson.mco@gmail.com>
