import dripline.core

def test_specifier_constructor():
    str_list = ["hi", "he-llo", ".", "1.", "5.6.7", ""]
    for s in str_list:
        item = dripline.core.Specifier(s)
        assert(item.to_string() == s)
    item = dripline.core.Specifier()
    assert(item.to_string() == "")

def test_parse():
    str_list = ["hi", "he-llo", ".", "1.", "5.6.7", ""]
    item = dripline.core.Specifier()
    for s in str_list:
        item.parse(s)
        assert(item.to_string() == s)


def test_reparse():
    str_list = ["hi", "he-llo", ".", "1.", "5.6.7", ""]
    item = dripline.core.Specifier()
    item.reparse()
    assert(item.to_string() == "")
    for s in str_list:
        item.parse(s)
        item.reparse()
        assert(item.to_string() == s)
