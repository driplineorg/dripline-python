import dripline.core

def test_builtin_ret_code():
    default = None
    builtin_ret_codes = dripline.get_return_code_values()
    builtin_ret_codes_map = dripline.get_return_codes_map()
    for ret_code in builtin_ret_codes:
        ret_code_obj = builtin_ret_codes_map.get(ret_code, default)
        assert(ret_code_obj != default)
        assert(ret_code_obj.value() >= 0)
        assert(ret_code_obj.name().startswith("DL_"))

def test_add_unique_ret_codes():
    num = 10
    default = None
    base_value = 1000
    base_name = "new"
    base_description = "this is a description for new"
    for i in range(num):
        value = base_value + i
        name = base_name + str(i)
        description = base_description + str(i)
        dripline.add_return_code(value, name, description)
    new_ret_codes = dripline.core.get_return_code_values()
    new_ret_codes_map = dripline.core.get_return_codes_map()
    for i in range(num):
        ret_code_obj = new_ret_codes_map.get(base_value + i, default)
        assert(ret_code_obj != default)
        assert(ret_code_obj.value() == base_value + i)
        assert(ret_code_obj.name() == "DL_" + (base_name + str(i)).upper())
        assert(ret_code_obj.description() == base_description + str(i))

def test_add_duplicated_ret_codes():
    value1 = 2001
    name1 = "name1"
    description1 = "description1"
    name2 = "name2"
    description2 = "description2"    
    dripline.core.add_return_code(value1, name1, description1)
    flag = False
    try:
        dripline.add_return_code(value1, name2, description2)
    except RuntimeError:
        flag = True
    assert(flag)
