import os

import pandana.network as pdna

# Pandana uses global state for networks,
# so we have to pre-declare here how many networks will be
# created during testing.
#
# If you see an error that looks like:
#     AssertionError: Adding more networks than have been reserved
# then you probably need to update this number.
#
# The tests seem to crash on Travis when more than one Network is made,
# so always have one Network there.
# If you add new tests that create a Network you'll need to mark them
# so they are skipped on Travis. E.g.:
#
#     @pytest.mark.skipif(
#         os.environ.get('TRAVIS') == 'true', reason='skip on Travis-CI')
#     def test_network_from_bbox(bbox2):
#
# You'll also need to increment the non-Travis number of tests below
# to match the number of Networks created while running tests locally.

if os.environ.get('TRAVIS') == 'true':
    num_networks_tested = 1
else:
    num_networks_tested = 5

pdna.reserve_num_graphs(num_networks_tested)
