import os
import glob
import json
import collections.abc as collections
from typing import Dict, List, Type, Union, Optional, MutableMapping, Text, Any
import yaml


class Gestalt:
    def __init__(self) -> None:
        """ Creates the default configuration manager

        The default settings are as follows:
         - Supports JSON and YAML files types. YAML file types are prioritized
            - Files in a directory are loaded in alphabetical order for determinism
         - Single config files are prioritized over config directories, regardless of format
         - Environment variables disabled
         - Configuration delimiter is '.'
         - No environment variables prefix
        """
        self.__conf_data: Dict[Text, Union[List[Any], Text, int, bool,
                                           float]] = dict()
        self.__conf_file_name: Text = '*'
        self.__conf_file_paths: List[str] = []
        self.__conf_files: List[str] = []
        self.__use_env: bool = False
        self.__env_prefix: Text = ''
        self.__delim_char: Text = '.'
        self.__conf_sets: Dict[Text, Union[List[Any], Text, int, bool,
                                           float]] = dict()
        self.__conf_defaults: Dict[Text, Union[List[Any], Text, int, bool,
                                               float]] = dict()

    def __flatten(
        self,
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
        """Adds a path to read configs from.

        Configurations are read in the order they are added in, and overlapping keys are
        overwritten in that same order, so the last config path added has the highest
        priority.

        The provided path argument can contain environment variables and also be relative,
        the library will expand this into an absolute path.

        Args:
            path (str): Path from which to load configuration files

        Raises:
            ValueError: If the `path` does not exist or is it not a directory
        """
        tmp = os.path.abspath(os.path.expandvars(path))
        if not os.path.exists(tmp):
            raise ValueError(f'Given directory path of {tmp} does not exist')
        if not os.path.isdir(tmp):
            raise ValueError(
                f'Given directory path of {tmp} is not a directory')
        self.__conf_file_paths.append(tmp)

    def add_config_file(self, path: str) -> None:
        """Adds a path to a single file to read configs from

        Configurations are read in the order they are added in, and overlapping keys are
        overwritten in that same order, so the last config file added has the highest
        priority. Single config files have higher priority than config directories

        The provided path argument can contain environment variables and also be relative,
        the library will expand this into an absolute path.

        Args:
            path (str): Path from which to load a configuration file

        Raises:
            ValueError: If the `path` does not exist or is it not a file
        """
        tmp = os.path.abspath(os.path.expandvars(path))
        if not os.path.exists(tmp):
            raise ValueError(f'Given file path of {tmp} does not exist')
        if not os.path.isfile(tmp):
            raise ValueError(f'Given file path of {tmp} is not a file')
        self.__conf_files.append(tmp)

    def build_config(self) -> None:
        """Renders all configuration paths into the internal data structure

        This does not affect if environment variables are used, it just deals
        with the files that need to be loaded.
        """
        for p in self.__conf_file_paths:
            json_files = glob.glob(p + f'/{self.__conf_file_name}.json')
            json_files.sort()
            yaml_files = glob.glob(p + f'/{self.__conf_file_name}.yaml')
            yaml_files.sort()
            for json_file in json_files:
                with open(json_file) as jf:
                    try:
                        json_dict = json.load(jf)
                        self.__conf_data.update(json_dict)
                    except json.JSONDecodeError as e:
                        raise ValueError(
                            f'File {json_file} is marked as ".json" but cannot be read as such: {e}'
                        )
            for yaml_file in yaml_files:
                with open(yaml_file) as yf:
                    try:
                        yaml_dict = yaml.load(yf, Loader=yaml.FullLoader)
                        self.__conf_data.update(yaml_dict)
                    except yaml.YAMLError as e:
                        raise ValueError(
                            f'File {yaml_file} is marked as ".yaml" but cannot be read as such: {e}'
                        )

        for f in self.__conf_files:
            f_ext = f[-4:]
            if f_ext == 'json':
                try:
                    with open(f) as jf:
                        json_dict = json.load(jf)
                        self.__conf_data.update(json_dict)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f'File {f} is marked as ".json" but cannot be read as such: {e}'
                    )
            elif f_ext == 'yaml':
                try:
                    with open(f) as yf:
                        yaml_dict = yaml.load(yf, Loader=yaml.FullLoader)
                        self.__conf_data.update(yaml_dict)
                except yaml.YAMLError as e:
                    raise ValueError(
                        f'File {f} is marked as ".yaml" but cannot be read as such: {e}'
                    )

        self.__conf_data = self.__flatten(self.__conf_data,
                                          sep=self.__delim_char)

    def auto_env(self) -> None:
        """Auto env provides sane defaults for using environment variables

        Specifically, auto_env will enable the use of environment variables and
        will also clear the prefix for environment variables.
        """
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
        if key in self.__conf_data and not isinstance(self.__conf_data[key],
                                                      t):
            raise TypeError(
                f'File config has {key} with type {type(self.__conf_data[key])}. \
                    Setting key with type {t} is not permitted')
        if key in self.__conf_defaults and not isinstance(
                self.__conf_defaults[key], t):
            raise TypeError(
                f'Default config has {key} with type {type(self.__conf_defaults[key])}. \
                    Setting key with type {t} is not permitted')
        if key in self.__conf_sets and not isinstance(self.__conf_sets[key],
                                                      t):
            raise TypeError(
                f'Overriding key {key} with type {type(self.__conf_sets[key])} with a {t} is not permitted'
            )
        self.__conf_sets[key] = value

    def set_string(self, key: str, value: str) -> None:
        """Sets the override string configuration for a given key

        Args:
            key (str): The key to override
            value (str): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of string type. Also
            raised if the key sets value for a differing type.
        """
        self.__set(key, value, str)

    def set_int(self, key: str, value: int) -> None:
        """Sets the override int configuration for a given key

        Args:
            key (str): The key to override
            value (int): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of int type. Also
            raised if the key sets value for a differing type.
        """
        self.__set(key, value, int)

    def set_float(self, key: str, value: float) -> None:
        """Sets the override float configuration for a given key

        Args:
            key (str): The key to override
            value (float): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of float type. Also
            raised if the key sets value for a differing type.
        """
        self.__set(key, value, float)

    def set_bool(self, key: str, value: bool) -> None:
        """Sets the override boolean configuration for a given key

        Args:
            key (str): The key to override
            value (bool): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of bool type. Also
            raised if the key sets value for a differing type.
        """
        self.__set(key, value, bool)

    def set_list(self, key: str, value: List[Any]) -> None:
        """Sets the override list configuration for a given key

        Args:
            key (str): The key to override
            value (list): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of list type. Also
            raised if the key sets value for a differing type.
        """
        self.__set(key, value, list)

    def __set_default(
            self, key: str, value: Union[str, int, float, bool, List[Any]],
            t: Type[Union[str, int, float, bool, List[Any]]]) -> None:
        if not isinstance(key, str):
            raise TypeError(f'Given key is not of string type')
        if not isinstance(value, t):
            raise TypeError(
                f'Input value when setting default {t} of type {type(value)} is not permitted'
            )
        if key in self.__conf_data and not isinstance(self.__conf_data[key],
                                                      t):
            raise TypeError(
                f'File config has {key} with type {type(self.__conf_data[key])}. \
                    Setting default with type {t} is not permitted')
        if key in self.__conf_sets and not isinstance(self.__conf_sets[key],
                                                      t):
            raise TypeError(
                f'Set config has {key} with type {type(self.__conf_sets[key])}. \
                    Setting key with type {t} is not permitted')
        if key in self.__conf_defaults and not isinstance(
                self.__conf_defaults[key], t):
            raise TypeError(f'Overriding default key {key} \
                    with type {type(self.__conf_defaults[key])} with a {t} is not permitted'
                            )
        self.__conf_defaults[key] = value

    def set_default_string(self, key: str, value: str) -> None:
        """Sets the default string configuration for a given key

        Args:
            key (str): The key to override
            value (str): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of string type. Also
            raised if the key sets default for a differing type.
        """
        self.__set_default(key, value, str)

    def set_default_int(self, key: str, value: int) -> None:
        """Sets the default int configuration for a given key

        Args:
            key (str): The key to override
            value (int): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of int type. Also
            raised if the key sets default for a differing type.
        """
        self.__set_default(key, value, int)

    def set_default_float(self, key: str, value: float) -> None:
        """Sets the default float configuration for a given key

        Args:
            key (str): The key to override
            value (float): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of float type. Also
            raised if the key sets default for a differing type.
        """
        self.__set_default(key, value, float)

    def set_default_bool(self, key: str, value: bool) -> None:
        """Sets the default boolean configuration for a given key

        Args:
            key (str): The key to override
            value (bool): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of bool type. Also
            raised if the key sets default for a differing type.
        """
        self.__set_default(key, value, bool)

    def set_default_list(self, key: str, value: List[Any]) -> None:
        """Sets the default list configuration for a given key

        Args:
            key (str): The key to override
            value (list): The configuration value to store

        Raises:
            TypeError: If the `key` is not a string or `value` is not of list type. Also
            raised if the key sets default for a differing type.
        """
        self.__set_default(key, value, list)

    def __get(
        self, key: str, default: Optional[Union[str, int, float, bool,
                                                List[Any]]],
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
        """Gets the configuration string for a given key

        Args:
            key (str): The key to get
            default (Optional: string): Optional default value if a configuration does not exist

        Returns:
            string: The string value at the given `key`

        Raises:
            TypeError: If the `key` is not a string or `value` is not of string type. Raised if the
                environment variable cannot be coalesced to the needed type.
            ValueError: If the 'key' is not in any configuration and no default is provided
            RuntimeError: If the internal value was stored with the incorrect type. This indicates
                a serious library bug
        """
        val: Union[Text, int, float, bool,
                   List[Any]] = self.__get(key, default, str)
        if not isinstance(val, str):
            raise RuntimeError(
                f'Gestalt error: expected to return string, but got {type(val)}'
            )
        return val

    def get_int(self, key: str, default: Optional[int] = None) -> int:
        """Gets the configuration int for a given key

        Args:
            key (str): The key to get
            default (Optional: int): Optional default value if a configuration does not exist

        Returns:
            int: The int value at the given `key`

        Raises:
            TypeError: If the `key` is not a string or `value` is not of int type. Raised if the
                environment variable cannot be coalesced to the needed type.
            ValueError: If the 'key' is not in any configuration and no default is provided
            RuntimeError: If the internal value was stored with the incorrect type. This indicates
                a serious library bug
        """
        val: Union[Text, int, float, bool,
                   List[Any]] = self.__get(key, default, int)
        if not isinstance(val, int):
            raise RuntimeError(
                f'Gestalt error: expected to return string, but got {type(val)}'
            )
        return val

    def get_float(self, key: str, default: Optional[float] = None) -> float:
        """Gets the configuration float for a given key

        Args:
            key (str): The key to get
            default (Optional: float): Optional default value if a configuration does not exist

        Returns:
            float: The float value at the given `key`

        Raises:
            TypeError: If the `key` is not a string or `value` is not of float type. Raised if the
                environment variable cannot be coalesced to the needed type.
            ValueError: If the 'key' is not in any configuration and no default is provided
            RuntimeError: If the internal value was stored with the incorrect type. This indicates
                a serious library bug
        """
        val: Union[Text, int, float, bool,
                   List[Any]] = self.__get(key, default, float)
        if not isinstance(val, float):
            raise RuntimeError(
                f'Gestalt error: expected to return float, but got {type(val)}'
            )
        return val

    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        """Gets the configuration bool for a given key

        Args:
            key (str): The key to get
            default (Optional: bool): Optional default value if a configuration does not exist

        Returns:
            bool: The bool value at the given `key`

        Raises:
            TypeError: If the `key` is not a string or `value` is not of bool type. Raised if the
                environment variable cannot be coalesced to the needed type.
            ValueError: If the 'key' is not in any configuration and no default is provided
            RuntimeError: If the internal value was stored with the incorrect type. This indicates
                a serious library bug
        """
        val: Union[Text, int, float, bool,
                   List[Any]] = self.__get(key, default, bool)
        if not isinstance(val, bool):
            raise RuntimeError(
                f'Gestalt error: expected to return bool, but got {type(val)}')
        return val

    def get_list(self,
                 key: str,
                 default: Optional[List[Any]] = None) -> List[Any]:
        """Gets the configuration list for a given key

        Args:
            key (str): The key to get
            default (Optional: list): Optional default value if a configuration does not exist

        Returns:
            list: The list value at the given `key`

        Raises:
            TypeError: If the `key` is not a string or `value` is not of list type. Raised if the
                environment variable cannot be coalesced to the needed type.
            ValueError: If the 'key' is not in any configuration and no default is provided
            RuntimeError: If the internal value was stored with the incorrect type. This indicates
                a serious library bug
        """
        val: Union[Text, int, float, bool,
                   List[Any]] = self.__get(key, default, list)
        if not isinstance(val, list):
            raise RuntimeError(
                f'Gestalt error: expected to return list, but got {type(val)}')
        return val

    def dump(self) -> Text:
        """Formats the current set of configurations as a pretty printed JSON string

        Returns:
            str: JSON string representation
        """
        ret: Dict[str, Any] = self.__conf_defaults
        ret.update(self.__conf_data)
        ret.update(self.__conf_sets)
        return str(json.dumps(ret, indent=4))
