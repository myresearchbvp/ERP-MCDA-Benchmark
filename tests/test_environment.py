import sys, numpy, scipy
def test_python(): assert sys.version_info >= (3,11)
def test_numpy(): assert int(numpy.__version__.split('.')[0]) >= 2
def test_scipy(): assert int(scipy.__version__.split('.')[0]) >= 1
