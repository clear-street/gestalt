def parse_nested_dict_and_find_key(d, key):
    if not isinstance(d, dict):
        return None
    if key in d:
        return d[key]
    for k, v in d.items():
        if isinstance(v, dict):
            item = parse_nested_dict_and_find_key(v, key)
            if item is not None:
                return item
    return None