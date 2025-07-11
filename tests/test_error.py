import dripline
import pytest

def test_raise_dripline_error():
    with pytest.raises(dripline.core.DriplineError) as excinfo:
        raise dripline.core.DriplineError
    assert excinfo.type is dripline.core.DriplineError

def test_throw_dripline_error():
    message = "test_throw"
    with pytest.raises(dripline.core.DriplineError, match=message) as excinfo:
        dripline.core.throw_dripline_error(message)
    assert excinfo.type is dripline.core.DriplineError

# In dripline::core::do_send() we throw a dripline message object.
# Let's make sure that gets caught in a reasonable way from the Python side
def test_throw_message():
    with pytest.raises(RuntimeError) as excinfo:
        dripline.core.throw_message()
    print(f'Exception value: {excinfo.value}')
    assert excinfo.type is RuntimeError
