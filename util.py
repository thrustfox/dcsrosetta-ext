def format_keys(keys: set) -> str:
    return ", ".join(sorted(keys))


def check_keys_match(dict1: dict, dict2: dict) -> bool:
    """
    check two dicts have same key list
    """
    dict1_empty = not dict1
    dict2_empty = not dict2

    if dict1_empty and dict2_empty:
        return True
    if dict1_empty or dict2_empty:
        return False

    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    added_keys   = keys2 - keys1
    removed_keys = keys1 - keys2

    if added_keys or removed_keys:
        print("")
    if added_keys:
        print(f"Added IDs in Excel: {format_keys(added_keys)}")
    if removed_keys:
        print(f"Omitted IDs in Excel: {format_keys(removed_keys)}")

    return not (added_keys or removed_keys)


def merge_dicts(a: dict, b: dict) -> dict:
    if not a or not b:
        return {}

    c = b.copy()
    for key in a:
        if key not in b:
            c[key] = a[key]
    return c
