import pytest
from app.models import Event

@pytest.mark.parametrize('key, id', [
    (  0, 'A-01'),
    (  1, 'B-01'),
    (  2, 'C-01'),
    ( 19, 'Z-01'),
    ( 20, 'A-03'),
    ( 21, 'B-03'),
    ( 39, 'Z-03'),
    ( 40, 'A-05'),
    ( 41, 'B-05'),
    (999, 'Z-99')
])
def test_seller_id(key, id):
    assert id == Event.generate_seller_id(key)
