import os

import pytest

skipifci = pytest.mark.skipif(
    os.environ.get('CI') == 'true', reason='skip on CI')
