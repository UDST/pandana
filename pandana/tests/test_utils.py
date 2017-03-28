import pandas as pd
import pytest

from pandana.utils import reindex


@pytest.fixture
def node_df():
    data = {'node_id': [44, 55, 33, 22, 11],
            'x': [-122, -123, -124, -125, -126],
            'y': [37, 38, 39, 40, 41]}
    index = [1, 2, 3, 4, 5]

    df = pd.DataFrame(data, index)
    return df


@pytest.fixture
def result_series():
    data = {'value': [10, 20, 30, 40, 50]}
    index = [11, 22, 33, 44, 55]
    df = pd.DataFrame(data, index)
    df.index.name = 'id'
    s = pd.Series(df.value, df.index)
    return s


def test_reindex(node_df, result_series):

    reindexed_results = pd.DataFrame({'value': reindex(result_series,
                                                       node_df.node_id)})

    assert len(reindexed_results) == 5
    assert reindexed_results['value'][1] == 40
    assert reindexed_results['value'][5] == 10
