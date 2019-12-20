import os
import glob
import json
import collections.abc as collections
from typing import Dict, List, Type, Union, Optional, MutableMapping, Text, Any


class Gestalt:
    def __init__(self) -> None:
        self.__conf_data: Dict[
            Text, Union[List[Any], Text, int, bool, float]] = dict()
        self.__conf_file_format: Text = 'json'
        self.__conf_file_name: Text = '*'
        self.__conf_file_paths: List[str] = []
        self.__use_env: bool = False
        self.__env_prefix: Text = ''
        self.__delim_char: Text = '.'
        self.__conf_sets: Dict[
            Text, Union[List[Any], Text, int, bool, float]] = dict()
        self.__conf_defaults: Dict[
            Text, Union[List[Any], Text, int, bool, float]] = dict()

    def __flatten(self,
                  d: MutableMapping[Text, Any],
                  parent_key: str = '',
                  sep: str = '.'
                  ) -> Dict[Text, Union[List[Any], Text, int, bool, float]]:
        items: List[Any] = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self.__flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def add_config_path(self, path: str) -> None:
        tmp = os.path.abspath(path)
        print(tmp)
        if not os.path.lexists(tmp):
            raise ValueError(f'Given path of {path} does not exist')
        if not os.path.isdir(tmp):
            raise ValueError(f'Given path of {path} is not a directory')
        self.__conf_file_paths.append(tmp)

    def build_config(self) -> None:
        # Load all the files in path
        for p in self.__conf_file_paths:
            files = glob.glob(
                p + f'/{self.__conf_file_name}.{self.__conf_file_format}')
            for f in files:
                with open(f) as cf:
                    d = json.load(cf)
                    self.__conf_data.update(d)
        self.__conf_data = self.__flatten(self.__conf_data,
                                          sep=self.__delim_char)

    def auto_env(self) -> None:
        self.__use_env = True
        self.__env_prefix = ''

    def __set(self, key: str, value: Union[str, int, float, bool, List[Any]],
              t: Type[Union[str, int, float, bool, List[Any]]]) -> None:
        if not isinstance(key, str):
            raise TypeError(f'Given key is not of string type')
        if not isinstance(value, t):
            raise TypeError(
                f'Input value when setting {t} of type {type(value)} is not permitted'
            )
        if key in self.__conf_sets and not isinstance(self.__conf_sets[key],
                                                      t):
            raise TypeError(
                f'Overriding key {key} with type {type(self.__conf_sets[key])} with a {t} is not permitted'
            )
        self.__conf_sets[key] = value

    def set_string(self, key: str, value: str) -> None:
        self.__set(key, value, str)

    def set_int(self, key: str, value: int) -> None:
        self.__set(key, value, int)

    def set_float(self, key: str, value: float) -> None:
        self.__set(key, value, float)

    def set_bool(self, key: str, value: bool) -> None:
        self.__set(key, value, bool)

    def set_list(self, key: str, value: List[Any]) -> None:
        self.__set(key, value, list)

    def __set_default(self, key: str,
                      value: Union[str, int, float, bool, List[Any]],
                      t: Type[Union[str, int, float, bool, List[Any]]]
                      ) -> None:
        if not isinstance(key, str):
            raise TypeError(f'Given key is not of string type')
        if not isinstance(value, t):
            raise TypeError(
                f'Input value when setting default {t} of type {type(value)} is not permitted'
            )
        if key in self.__conf_defaults and not isinstance(
                self.__conf_defaults[key], t):
            raise TypeError(f'Overriding default key {key} \
                    with type {type(self.__conf_defaults[key])} with a {t} is not permitted'
                            )
        self.__conf_defaults[key] = value

    def set_default_string(self, key: str, value: str) -> None:
        self.__set_default(key, value, str)

    def set_default_int(self, key: str, value: int) -> None:
        self.__set_default(key, value, int)

    def set_default_float(self, key: str, value: float) -> None:
        self.__set_default(key, value, float)

    def set_default_bool(self, key: str, value: bool) -> None:
        self.__set_default(key, value, bool)

    def set_default_list(self, key: str, value: List[Any]) -> None:
        self.__set_default(key, value, list)

    def __get(self, key: str,
              default: Optional[Union[str, int, float, bool, List[Any]]],
              t: Type[Union[str, int, float, bool, List[Any]]]
              ) -> Union[str, int, float, bool, List[Any]]:
        if not isinstance(key, str):
            raise TypeError(f'Given key is not of string type')
        if default and not isinstance(default, t):
            raise TypeError(
                f'Provided default is of incorrect type {type(default)}, it should be of type {t}'
            )
        if key in self.__conf_sets:
            val = self.__conf_sets[key]
            if not isinstance(val, t):
                raise TypeError(
                    f'Given set key is not of type {t}, but of type {type(val)}'
                )
            return val
        if self.__use_env:
            e_key = key.upper().replace(self.__delim_char, '_')
            if e_key in os.environ:
                try:
                    return t(os.environ[e_key])
                except ValueError as e:
                    raise TypeError(
                        f'The environment variable {e_key} could not be converted to type {t}: {e}'
                    )
        if key in self.__conf_data:
            if not isinstance(self.__conf_data[key], t):
                raise TypeError(
                    f'The requested key of {key} is not of type {t} (it is {type(self.__conf_data[key])})'
                )
            return self.__conf_data[key]
        if default:
            return default
        if key in self.__conf_defaults:
            val = self.__conf_defaults[key]
            if not isinstance(val, t):
                raise TypeError(
                    f'Given default set key is not of type {t}, but of type {type(val)}'
                )
            return val
        raise ValueError(
            f'Given key {key} is not in any configuration and no default is provided'
        )

    def get_string(self, key: str, default: Optional[Text] = None) -> str:
        val: Union[Text, int, float, bool, List[Any]] = self.__get(
            key, default, str)
        if not isinstance(val, str):
            raise RuntimeError(
                f'Gestalt error: expected to return string, but got {type(val)}'
            )
        return val

    def get_int(self, key: str, default: Optional[int] = None) -> int:
        val: Union[Text, int, float, bool, List[Any]] = self.__get(
            key, default, int)
        if not isinstance(val, int):
            raise RuntimeError(
                f'Gestalt error: expected to return string, but got {type(val)}'
            )
        return val

    def get_float(self, key: str, default: Optional[float] = None) -> float:
        val: Union[Text, int, float, bool, List[Any]] = self.__get(
            key, default, float)
        if not isinstance(val, float):
            raise RuntimeError(
                f'Gestalt error: expected to return float, but got {type(val)}'
            )
        return val

    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        val: Union[Text, int, float, bool, List[Any]] = self.__get(
            key, default, bool)
        if not isinstance(val, bool):
            raise RuntimeError(
                f'Gestalt error: expected to return bool, but got {type(val)}')
        return val

    def get_list(self, key: str,
                 default: Optional[List[Any]] = None) -> List[Any]:
        val: Union[Text, int, float, bool, List[Any]] = self.__get(
            key, default, list)
        if not isinstance(val, list):
            raise RuntimeError(
                f'Gestalt error: expected to return list, but got {type(val)}')
        return val

    def dump(self) -> Text:
        return str(json.dumps(self.__conf_data, indent=4))
