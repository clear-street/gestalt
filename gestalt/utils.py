from typing import MutableMapping, Text, Any, Union, Dict, List
import collections.abc as collections


def flatten(
        d: MutableMapping[Text, Any],
        parent_key: str = '',
        sep: str = '.'
) -> Dict[Text, Union[List[Any], Text, int, bool, float]]:
    items: List[Any] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)