import pandana.network as pdna

# Pandana uses global state for networks,
# so we have to pre-declare here how many networks will be
# created during testing.
#
# If you see an error that looks like:
#     AssertionError: Adding more networks than have been reserved
# then you probably need to update this number.
num_networks_tested = 2
pdna.reserve_num_graphs(num_networks_tested)
