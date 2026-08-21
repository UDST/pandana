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


def migrate_legacy_hdf(filename, output_filename=None):
    """
    Normalize legacy Pandas HDF5 metadata written as byte strings.

    Older Pandas/PyTables combinations stored attributes such as
    ``pandas_type`` as bytes. Pandas 3 expects text when it reconstructs
    storers. This utility explicitly migrates those attributes either in
    place or into ``output_filename`` if one is supplied.
    """
    try:
        import tables
    except ImportError:
        return None

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


def _pandas_can_read(filename):
    """Return True if Pandas can open every table in the file as-is."""
    try:
        with pd.HDFStore(filename, mode="r") as store:
            for key in store.keys():
                store.get_storer(key)
    except Exception:
        return False
    return True


@contextmanager
def open_hdf_store(filename, mode="r", migrate_legacy=False):
    """
    Open a Pandas HDFStore, handling files written by older Pandas versions.

    Pandana network files saved with older Pandas/PyTables combinations have
    metadata stored as byte strings, which Pandas 3 can no longer read. This
    context manager opens the file normally when Pandas can read it. If it
    can't and the file has legacy metadata, the file is either migrated into
    a temporary copy for the duration of the read (``migrate_legacy=True``),
    or a ``ValueError`` is raised explaining how to migrate the file with
    :func:`migrate_legacy_hdf`.

    Parameters
    ----------
    filename : str
    mode : str, optional
        Passed to ``pandas.HDFStore``. Legacy handling only applies to
        read mode.
    migrate_legacy : bool, optional
        If True, migrate legacy metadata into a temporary copy when Pandas
        can't read the file directly. The default is False so large network
        files are not copied implicitly.

    Yields
    ------
    store : pandas.HDFStore

    """
    temp_filename = None
    store_filename = filename

    needs_migration = False
    if mode == "r" and not _pandas_can_read(filename):
        needs_migration = _has_legacy_pandas_attrs(filename)

    if needs_migration:
        if not migrate_legacy:
            raise ValueError(
                "This file has legacy Pandas HDF5 metadata that the "
                "installed version of Pandas can't read. Run "
                "pandana.loaders.pandash5.migrate_legacy_hdf(...) to "
                "migrate it, or pass migrate_legacy=True to read from a "
                "temporary migrated copy."
            )
        fd, temp_filename = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        store_filename = migrate_legacy_hdf(filename, temp_filename)

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


def network_from_pandas_hdf5(cls, filename, migrate_legacy=False):
    """
    Build a Network from data in a Pandas HDFStore.

    Parameters
    ----------
    cls : class
        Class to instantiate, usually pandana.Network.
    filename : str
    migrate_legacy : bool, optional
        If True and the installed Pandas can't read the file's legacy
        metadata, migrate it into a temporary copy before reading. The
        default is False so large network files are not copied implicitly.

    Returns
    -------
    network : pandana.Network

    """
    with open_hdf_store(filename, migrate_legacy=migrate_legacy) as store:
        nodes = store['nodes']
        edges = store['edges']
        two_way = store['two_way'][0]
        imp_names = store['impedance_names'].tolist()

    return cls(
        nodes['x'], nodes['y'], edges['from'], edges['to'], edges[imp_names],
        twoway=two_way)
