import os

import pytest

travis = os.environ.get('TRAVIS') == 'true'
appveyor = os.environ.get('APPVEYOR') == 'True'

ci_condition = travis or appveyor

skipifci = pytest.mark.skipif(ci_condition, reason='skip on CI build')
