import dripline
import pytest

def test_log_a_value():
    a_service = dripline.core.Service("hello", make_connection=False)
    a_entity = dripline.core.Entity(name="ent")
    a_service.add_child(a_entity)
    with pytest.raises(RuntimeError) as excinfo:
        a_entity.log_a_value(5)
    assert excinfo.type is RuntimeError
    assert "Thrown alert:" in str(excinfo.value)
    assert "Payload: 5" in str(excinfo.value)
