import numpy as np
def test_coord_array(h2o_dimer):
    arr = h2o_dimer.coord_array()
    assert np.shape(arr) == (6,3)
