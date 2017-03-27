import pandas as pd
import pytest

from pandana.utils import reindex


@pytest.fixture
def dataframe():
    data = {'node_id': [44, 55, 33, 22, 11],
            'x': [-122, -123, -124, -125, -126],
            'y': [37, 38, 39, 40, 41]}
    index = [1, 2, 3, 4, 5]

    df = pd.DataFrame(data, index)
    return df


@pytest.fixture
def series():
    data = {'value': [10, 20, 30, 40, 50]}
    index = [11,22,33,44,55]
    df = pd.DataFrame(data, index)
    df.index.name = 'id'
    s = pd.Series(df.value, df.index)
    return s


def test_reindex(dataframe, series):

    results = pd.DataFrame({'value': reindex(series, dataframe.node_id)})

    assert len(results) == 5
    assert results['value'][1] == 40
    assert results['value'][5] == 10