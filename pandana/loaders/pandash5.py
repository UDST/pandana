import os
import shutil
import tempfile
from contextlib import contextmanager

import pandas as pd


def _has_legacy_pandas_attrs(filename):
    try:
        import tables
    except ImportError:
        return False

    with tables.open_file(filename, mode="r") as h5:
        for node in h5.walk_nodes("/"):
            attrs = node._v_attrs
            for name in attrs._v_attrnames:
                value = getattr(attrs, name)
                if not isinstance(value, str) and hasattr(value, "decode"):
                    return True

    return False


def _decode_legacy_pandas_attrs(filename, output_filename=None):
    """
    Normalize legacy Pandas HDF5 metadata written as byte strings.

    Older Pandas/PyTables combinations stored attributes such as
    ``pandas_type`` as bytes. Pandas 3 expects text when it reconstructs
    storers, so decode those attributes before opening the file with
    ``pd.HDFStore``.
    """
    try:
        import tables
    except ImportError:
        return

    target = output_filename or filename
    if output_filename is not None:
        shutil.copyfile(filename, output_filename)

    with tables.open_file(target, mode="a") as h5:
        for node in h5.walk_nodes("/"):
            attrs = node._v_attrs
            for name in attrs._v_attrnames:
                value = getattr(attrs, name)
                if isinstance(value, str) or not hasattr(value, "decode"):
                    continue

                setattr(attrs, name, value.decode("utf-8"))

    return target


@contextmanager
def _legacy_compatible_hdf_store(filename, mode="r"):
    temp_filename = None
    store_filename = filename

    if mode == "r" and _has_legacy_pandas_attrs(filename):
        fd, temp_filename = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        store_filename = _decode_legacy_pandas_attrs(filename, temp_filename)

    try:
        with pd.HDFStore(store_filename, mode=mode) as store:
            yield store
    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)


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
    with _legacy_compatible_hdf_store(filename) as store:
        nodes = store['nodes']
        edges = store['edges']
        two_way = store['two_way'][0]
        imp_names = store['impedance_names'].tolist()

    return cls(
        nodes['x'], nodes['y'], edges['from'], edges['to'], edges[imp_names],
        twoway=two_way)
