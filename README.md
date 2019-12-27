# Gestalt

> Gestalt (/ɡəˈSHtält/) - _noun_ - an organized whole that is perceived as more than the sum of its parts.

Gestalt is an opinionated, strongly typed, configuration library for Python 3.6+. Gestalt aims to simplify configuration loading, getting/setting, and management by letting the user focus on writing programs, and letting Gestalt check configuration types, location, and environment variable overrides.



## Install

```python
pip install gestalt
```

## Why use Gestalt?

In short, Gestalt does the following:

1. Automatically loads configuration files from a directory
2. Allows for runtime overrides
3. Allows for runtime defaults
4. Allows for default values when trying to get a config
5. Allows for environment variable overrides
6. Type checks _everything_

Specifically, Gestalt enforces configs in the following order:

1. Calls to `set_*`
2. Environment Variables
3. Config Files
4. Defaults provided in `get_*`
5. Set default values

## Usage

### TL;DR

```python
from gestalt import gestalt

g = gestalt.Gestalt()
g.add_config_path('./testdata')
g.build_config()

my_val_1 = g.get_string('some.nested.string')
my_val_2 = g.get_int('someint')
my_val_3 = g.get_float('somekey', 57.29) # If 'somekey' doesn't exist, retrun default value

g.set_bool('my_custom_config', True)
g.get_list('my_custom_config') # Raises TypeError, as this key is a bool, and we asked for a list
```

### Initialization

Beginning to use Gestalt is as simple as:

```python
from gestalt import gestalt

g = gestalt.Gestalt()
```

### Loading Configuration Files

Loading a directory of configuration files is done by calling `add_config_path`

```python
g.add_config_path('./testdata')
```

Multiple directory paths can be added:

```python
g.add_config_path('./testdata2')
g.add_config_path('./testdata3')
```

After all the directory paths are added, we can render them:

```python
g.build_config()
```

Note that the the last added directory path takes the most precedence, and will override conflicting keys from previous paths. In addition to this, the rendering flattens the config, for example, the configuration:

```json
{
  "yarn": "blue skies",
  "numbers": 12345678,
  "strangenumbers": 123.456,
  "truthy": true,
  "listing": ["dog", "cat"],
  "deep": {
    "nested1": "hello",
    "nested2": "world"
  }
}

```

Will be rendered to this in the internal data structure:

```json
{
    "yarn": "blue skies",
    "numbers": 12345678,
    "strangenumbers": 123.456,
    "truthy": true,
    "listing": [
        "dog",
        "cat"
    ],
    "deep.nested1": "hello",
    "deep.nested2": "world"
}

```

The nested values are flattened and delimited by periods, making access simpler. **Note**, Gestalt will not normalize names in config files, so keys are case sensitive.

### Environment Variables

Environment variable overrides are not enabled by default. To enable it:

```python
g.auto_env()
```

With this, Gestalt will check to see if a corresponding environment variable exists, for example if checking for the key `some.nested.key`, Gestalt will search for `SOME_NESTED_KEY`, and attempt to convert it to the desired type.

### Setting and Getting Values

#### Types

Currently, Gestalt supports 5 basic types:

1. String
2. Int
3. Float
4. Bool
5. List

For each of these types, there is a corresponding `get` and `set` function, allowing for Gestalt to guarantee types.

#### Setting

To set a configuration value programmatically:

```python
g.set_string('some.k', 'value')
```

Defined by the function signature:

```python
set_string(self, key: str, value: str) -> None
```

The same applies to the remaining types that Gestalt supports:

```python
set_int(key: str, value: int) -> None
set_float(key: str, value: float) -> None
set_bool(key: str, value: bool) -> None
set_list(key: str, value: List[Any]) -> None
```

Note that all of these functions, in addition from being type hinted, also strongly enforce types, and will raise TypeErrors in the following cases:

1. Setting a key that is not a string
2. Setting a value that does not match the function signature
3. Overriding an existing set value of type `a` with type `b`

#### Setting Default Values

To set a default configuration value programmatically:

```python
g.set_defualt_string('some.default.k', 'default value')
```
Defined by the function signature

```python
set_default_string(key: str, value: str) -> None
```
The same applies to the remaining types that Gestalt supports:

```python
set_default_int(key: str, value: int) -> None
set_default_float(key: str, value: float) -> None
set_default_bool(key: str, value: bool) -> None
set_default_list(key: str, value: List[Any]) -> None
```

Note that all of these functions, in addition from being type hinted, also strongly enforce types, and will raise TypeErrors in the following cases:

1. Setting a key that is not a string
2. Setting a value that does not match the function signature
3. Overriding an existing default set value of type `a` with type `b`

#### Getting Values

To get a configuration value:

```python
g.get_string('some.key')
```

This will attempt to retrieve the given key from the configuration, in order of precedence. If no such key exists in all configurations, a `ValueError` will be raised.

In addition to this, a default can be passed:

```python
g.get_string('some.key', 'some default value')
```

The `get` function will raise `TypeError`s in the following cases:

1. The key is not a string
2. The default value does not match the desired type
3. The configuration has the key with a value of type `a`, when the user desires a value of type `b`