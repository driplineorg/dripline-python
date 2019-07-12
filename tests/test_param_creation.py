import scarab

def test_type_checks():
    a_param = scarab.ParamValue(3)
    assert isinstance(a_param, scarab.Param)
