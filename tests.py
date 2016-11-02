import unittest
from measure_field import Measure, Unit

class TestMeasureField(unittest.TestCase):

    def test_instance(self):
        t = Measure(cm=1)
        self.assertEqual(str(t), '1.0 cm')

    def test_simple_conversion(self):
        t = Measure(cm=1)
        # long conversion
        t2 = t.convert(cm=Unit.mm)
        self.assertEqual(t2.value, 10)
        # short conversion
        self.assertEqual(t.mm.value, 10)
        self.assertEqual(t.m.value, 0.01)
    
    def test_complex_conversion(self):
        t = Measure()
        
        #1 m2 to cm2
        t.value = 1
        t.units[Unit.m] = 2

        self.assertEqual(t.cm.value, 10000)

        #1 m/s to cm/s
        t.value = 1
        t.units[Unit.m] = 1
        t.units[Unit.s] = -1
        self.assertEqual(t.convert(m=Unit.cm).value, 100.)
        #1 m/s to m/min
        self.assertEqual(t.convert(s=Unit.minute).value, 60.0)
        #1 m/s to cm/min
        self.assertEqual(t.convert(s=Unit.minute, m=Unit.cm).value, 6000)

        #1 m/s^2 to  km/hour^2
        t.value = 1
        t.units[Unit.m] = 1
        t.units[Unit.s] = -2
        self.assertEqual(t.convert(m=Unit.km, s=Unit.hour).value, 12960)

        
    def test_add(self):
        t1 = Measure(cm=1)
        t2 = Measure(mm=10)
        res = t1 + t2
        self.assertEqual(res.value, 2)
        self.assertEqual(res.units[Unit.cm], 1)

    def test_mult(self):
        t = Measure(cm=1)

        self.assertEqual((t * 2).value, 2)

        t = Measure(cm=4)
        tt =t * t
        self.assertEqual(tt.value, 16)
        self.assertEqual(tt.units[Unit.cm], 2)
        
        ttt = t * t * t
        self.assertEqual(ttt.value, 64)
        self.assertEqual(ttt.units[Unit.cm], 3)

        #Complex mult 4 m/s *  2s = 8m
        t1 = Measure()
        t1.value = 4
        t1.units = {Unit.m: 1, Unit.s: -1}
        t2 = Measure()
        t2.value = 2
        t2.units = {Unit.s: 1}

        r = t1 * t2
        self.assertEqual(r.value, 8)
        self.assertEqual(r.units[Unit.m], 1)
        self.assertEqual(Unit.s in r.units, False)

    def test_div(self):
        t = Measure(cm=1)
        self.assertEqual((t/2.).value, 0.5)


        self.assertEqual( (t/t).value, 1)

        
        self.assertEqual((4./t).value, 4.)
        self.assertEqual((4./t).units[Unit.cm], -1)

        t1 = Measure(cm=1)
        t2 = Measure(cm=2)

        self.assertEqual((t1 / t2).value, 0.5)
        self.assertEqual((t1 / t2).units, {})

        t1 = Measure(cm=1)
        t1 = t1 * t1
        t2 = Measure(cm=2)

        self.assertEqual((t1 / t2).value, 0.5)
        self.assertEqual((t1 / t2).units[Unit.cm], 1)

    def test_pow(self):
        t = Measure(cm=2)
        r = t ** 3
        self.assertEqual(r.value, 8)
        self.assertEqual(r.units[Unit.cm] , 3)

if __name__ == '__main__':
    unittest.main()
