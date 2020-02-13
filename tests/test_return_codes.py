import scarab, _dripline.core

def test_builtin_ret_code():
    default = None
    builtin_ret_codes = _dripline.core.get_return_code_values()
    builtin_ret_codes_map = _dripline.core.get_return_codes_map()
    for ret_code in builtin_ret_codes:
        ret_code_obj = builtin_ret_codes_map.get(ret_code, default)
        assert(ret_code_obj != default)
        assert(type(ret_code_obj.value) is int and ret_code_obj.value >= 0)
        assert(type(ret_code_obj.name) is str)
        assert(type(ret_code_obj.description) is str)

def test_add_unique_ret_codes():
    num = 10
    default = None
    base_value = 1000
    base_name = "new error"
    base_description = "this is a description for new error"
    for i in range(num):
        value = base_value + i
        name = base_name + str(i)
        description = base_description + str(i)
        _dripline.core.add_return_code(value, name, description)
    new_ret_codes = _dripline.core.get_return_code_values()
    new_ret_codes_map = _dripline.core.get_return_codes_map()
    for i in range(num):
        ret_code_obj = new_ret_codes_map.get(base_value + i, default)
        assert(ret_code_obj != default)
        assert(type(ret_code_obj.value) is int and ret_code_obj.value == base_value + i)
        assert(type(ret_code_obj.name) is str and ret_code_obj.name == (base_name + str(i)))
        assert(type(ret_code_obj.description) is str and ret_code_obj.description == base_description + str(i))

def test_add_duplicated_ret_codes():
    value1 = 2000
    name1 = "name1"
    description1 = "description1"
    name2 = "name2"
    description2 = "description2"    
    _dripline.core.add_return_code(value1, name1, description1)
    flag = False
    try:
        _dripline.core.add_return_code(value1, name2, description2)
    except RuntimeError:
        flag = True
    assert(flag)
