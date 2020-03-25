import chaospy as cp
import easyvvuq as uq
import pytest
import numpy as np

@pytest.fixture
def sc_sampler():
    vary = {
        "Pe" : cp.Uniform(100.0, 200.0),
        "f" : cp.Uniform(0.95, 1.05)
    }
    sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=[2, 5], quadrature_rule="G")
    return sampler

def test_generate_grid(sc_sampler):
    grid = sc_sampler.generate_grid(5, 2, np.array([[2, 5]]))
    assert((grid == np.array([(111.27016653792582, 0.9533765242898424),
                                (111.27016653792582, 0.9669395306766867),
                                (111.27016653792582, 0.98806904069584),
                                (111.27016653792582, 1.01193095930416),
                                (111.27016653792582, 1.033060469323313),
                                (111.27016653792582, 1.046623475710158),
                                (150.0, 0.9533765242898424),
                                (150.0, 0.9669395306766867),
                                (150.0, 0.98806904069584),
                                (150.0, 1.01193095930416),
                                (150.0, 1.033060469323313),
                                (150.0, 1.046623475710158),
                                (188.72983346207417, 0.9533765242898424),
                                (188.72983346207417, 0.9669395306766867),
                                (188.72983346207417, 0.98806904069584),
                                (188.72983346207417, 1.01193095930416),
                                (188.72983346207417, 1.033060469323313),
                                (188.72983346207417, 1.046623475710158)])).all())

def test_cmpute_sparse_multi_idx(sc_sampler):
    assert((sc_sampler.compute_sparse_multi_idx(5, 2) == np.array([[1, 1],
                                                                    [1, 2],
                                                                    [1, 3],
                                                                    [1, 4],
                                                                    [2, 1],
                                                                    [2, 2],
                                                                    [2, 3],
                                                                    [3, 1],
                                                                    [3, 2],
                                                                    [4, 1]])).all())
