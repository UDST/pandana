import pandas as pd


def remove_nodes(network, rm_nodes):
    """
    Create DataFrames of nodes and edges that do not include specified nodes.

    Parameters
    ----------
    network : pandana.Network
    rm_nodes : array_like
        A list, array, Index, or Series of node IDs that should *not*
        be saved as part of the Network.

    Returns
    -------
    nodes, edges : pandas.DataFrame

    """
    rm_nodes = set(rm_nodes)
    ndf = network.nodes_df
    edf = network.edges_df

    nodes_to_keep = ~ndf.index.isin(rm_nodes)
    edges_to_keep = ~(edf['from'].isin(rm_nodes) | edf['to'].isin(rm_nodes))

    return ndf.loc[nodes_to_keep], edf.loc[edges_to_keep]


def network_to_pandas_hdf5(network, filename, rm_nodes=None):
    """
    Save a Network's data to a Pandas HDFStore.

    Parameters
    ----------
    network : pandana.Network
    filename : str
    rm_nodes : array_like
        A list, array, Index, or Series of node IDs that should *not*
        be saved as part of the Network.

    """
    if rm_nodes is not None:
        nodes, edges = remove_nodes(network, rm_nodes)
    else:
        nodes, edges = network.nodes_df, network.edges_df

    with pd.HDFStore(filename, mode='w') as store:
        store['nodes'] = nodes
        store['edges'] = edges

        store['two_way'] = pd.Series([network._twoway])
        store['impedance_names'] = pd.Series(network.impedance_names)


def network_from_pandas_hdf5(cls, filename):
    """
    Build a Network from data in a Pandas HDFStore.

    Parameters
    ----------
    cls : class
        Class to instantiate, usually pandana.Network.
    filename : str

    Returns
    -------
    network : pandana.Network

    """
    with pd.HDFStore(filename) as store:
        nodes = store['nodes']
        edges = store['edges']
        two_way = store['two_way'][0]
        imp_names = store['impedance_names'].tolist()

    return cls(
        nodes['x'], nodes['y'], edges['from'], edges['to'], edges[imp_names],
        twoway=two_way)
