import os

import pytest

skipiftravis = pytest.mark.skipif(
    os.environ.get('TRAVIS') == 'true', reason='skip on Travis-CI')
