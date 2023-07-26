import pandas as pd


def reindex(series1, series2):
    """
    Reindex the first series by the second series.

    Parameters
    ----------
    series1 : pandas.Series
        Pandas series to reindex
    series2 : pandas.Series
        Pandas series to set the index of series1 by

    Returns
    -------
    df.right : pandas.DataFrame
    """

    # this function is identical to the reindex function found in UrbanSim in
    # urbansim/utils/misc.py
    df = pd.merge(pd.DataFrame({"left": series2}),
                  pd.DataFrame({"right": series1}),
                  left_on="left",
                  right_index=True,
                  how="left")
    return df.right


def adjacency_matrix(edges_df, plot_matrix=False):
    df = pd.crosstab(edges_df['from'], edges_df['to'])
    idx = df.columns.union(df.index)
    df = df.reindex(index=idx, columns=idx, fill_value=0)

    return df
