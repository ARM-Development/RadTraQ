import radtraq
import numpy as np


def test_calculate_dual_dop_lobes():
    d = {'Cullman': {'lat': 34.26274649951493, 'lon': -86.85874523934974},
         'Courtland': {'lat': 34.658302981847655, 'lon': -87.34389529761859}}

    data = radtraq.utils.calculate_dual_dop_lobes(d)

    assert 'lobe1' in data
    assert 'lobe2' in data

    np.testing.assert_almost_equal(data['lobe1']['lon'][0], -87.419, decimal=3)
    np.testing.assert_almost_equal(data['lobe2']['lat'][0], 34.106, decimal=3)
