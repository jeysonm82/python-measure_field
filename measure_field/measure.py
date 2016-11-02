from collections import namedtuple

class MeasureException(Exception):
    pass

ADIM = 0
LONGITUDE = 1
WEIGHT = 2
TIME = 3

UnitDef = namedtuple('UnitDef', ['name', 'long_name', 'unit_type', 'k'])

class Unit(object):
  mm = UnitDef(name='mm', long_name='milimeters', unit_type=LONGITUDE, k=1.)
  um = UnitDef(name='um', long_name='micrometre', unit_type=LONGITUDE, k=1e-3)
  cm = UnitDef(name='cm', long_name='centimeters', unit_type=LONGITUDE, k=10.)
  m = UnitDef(name='m', long_name='meters', unit_type=LONGITUDE, k=1000.)
  km = UnitDef(name='km', long_name='kilometers', unit_type=LONGITUDE, k=1e6)
  inch = UnitDef(name='in', long_name='inches', unit_type=LONGITUDE, k=25.4)
  
  gram = UnitDef(name='gram', long_name='grams', unit_type=WEIGHT, k=1.0)
  lb = UnitDef(name='lb', long_name='pounds', unit_type=WEIGHT, k=500.0)
  kg = UnitDef(name='kg', long_name='kilograms', unit_type=WEIGHT, k=1000.0)

  s = UnitDef(name='s', long_name='seconds', unit_type=TIME, k=1.0)
  minute = UnitDef(name='minute', long_name='minutes', unit_type=TIME, k=60.0)
  hour = UnitDef(name='hour', long_name='hours', unit_type=TIME, k=3600.0)
  day = UnitDef(name='day', long_name='days', unit_type=TIME, k=24 * 3600.0)
   
  # TODO add more units

  adim = UnitDef(name='adim', long_name='adimensional', unit_type=ADIM, k=1.)


class Measure(object):
    _prims = (int, float)

    '''
        self.units stores all units and respective dimensions of measure
        Ex:
        - 1m : {Unit.m: 1}
        - 1m^2: {Unit.m: 2}
        - 1m/s^2: {Unit.m: 1, Unit.s: 2}

    '''
    def __init__(self, *args, **kwargs):
        self.units = {}

        if len(kwargs):
            unit = getattr(Unit, kwargs.keys()[0])
            self.units[unit] = 1
            self.value = float(kwargs[unit.name])

    def __getattr__(self, tounit_name):
        # TODO only converting first unit in self.units to to_unit
        return self.convert(**{self.units.keys()[0].name: getattr(Unit, tounit_name)})

    def convert(self, **kwargs):
        '''Converts measure to given unit(s).'''

        newval = self.value
        to_units = self.units.copy()
        for uname in kwargs.keys():
            from_unit = getattr(Unit, uname)
            to_unit = kwargs[uname]
            if from_unit == to_unit:
                continue
            if to_unit.unit_type != from_unit.unit_type:
                raise MeasureException("Incompatible units %s to %s"%(from_unit.name, to_unit.name))

            dim = self.units[from_unit]
            newval = newval * ((from_unit.k / to_unit.k) ** dim)

            to_units[to_unit] = dim
            del to_units[from_unit]
        return self._ret_measure(newval, to_units)

    def _convert(self, to_unit_name):
        raise NotImplementedError

    
    def _ret_measure(self, value, units):
        m = Measure()
        m.units = units
        m.value = value
        return m

    def _to_same_units(self, measure):
        convert_dict = {}
        for u, v in measure.units.iteritems():
            for uu, vv in self.units.iteritems():
                if u.unit_type == uu.unit_type and u != uu:
                    convert_dict[u.name] = uu
                    break
        measure_converted = measure.convert(**convert_dict)
        return measure_converted

    def _multiply(self, other):
        if type(other) in self._prims:
            return self._ret_measure(self.value * other, self.units)
        #return self._ret_measure(self.value * other.value,CompUnitDef(unit_num=self.unit, unit_den=other.unit))
        other_conv = self._to_same_units(other)
        newval = self.value * other_conv.value
        #Update units's dims summing dimensions values in self.units and other.units
        all_units = set(self.units.keys() + other_conv.units.keys())
        final_units = {}
        for u in all_units:
            d = 0
            if u in self.units:
                d += self.units[u]
            if u in other_conv.units:
                d += other_conv.units[u]
            if d:
                final_units[u] = d
        
        return self._ret_measure(newval, final_units)

    def __mul__(self, other):
        return self._multiply(other)

    def __rmul__(self, other):
        return self._multiply(other)

    def _divide(self, other, left=True):
        if left:
            return self._multiply(1/other)
        else:
            # Invert all dims and value
            newval = 1 / self.value
            new_units = {k: v * -1 for k, v in self.units.iteritems()}
            return self._ret_measure(newval, new_units)._multiply(other)

    def __div__(self, other):
        return self._divide(other, True)

    def __rdiv__(self, other):
        return self._divide(other, False)

    def __add__(self, other):
        if type(other) in self._prims:
            raise MeasureException("Can't add these values %s + %s"%(self, other))

        #Convert other measure's units to this measure first
        other_converted = self._to_same_units(other)

        # Only can add measures with same units
        try:
            # all units must have same dimension (exponential)
            # We can compare now because other_converted has same units as self
            same_unitsdims_check = all([self.units[u] == v for u, v in other_converted.units.iteritems()])
            if not same_unitsdims_check:
                raise Exception
        except:
            raise MeasureException("Can't add these values %s + %s"%(self, other))


        newval = self.value + other_converted.value

        return self._ret_measure(newval, self.units) 

    def __pow__(self, other):
        if type(other) in self._prims:
            newval = self.value ** other
            new_units = self.units.copy()
            for u in new_units:
                new_units[u] *= other
            return self._ret_measure(newval, new_units)

        raise MeasureException("Can't pow these values %s + %s"%(self, other))

    def __str__(self):
        unit_text = '.'.join(["%s%s"%(u.name, '' if v==1 else '^%s'%(v)) for u, v in self.units.iteritems()])

        return "%s %s"%(self.value, unit_text)
    
    def __float__(self):
        return float(self.value)
    
    def __int__(self):
        return int(self.value)
