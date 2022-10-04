# Gestalt

![Builds](https://github.com/clear-street/gestalt/workflows/Python%20package/badge.svg) [![codecov](https://codecov.io/gh/clear-street/gestalt/branch/master/graph/badge.svg)](https://codecov.io/gh/clear-street/gestalt) [![PyPI download month](https://img.shields.io/pypi/dm/gestalt-cfg.svg)](https://pypi.python.org/pypi/gestalt-cfg/) [![PyPI version shields.io](https://img.shields.io/pypi/v/gestalt-cfg.svg)](https://pypi.python.org/pypi/gestalt-cfg/) [![PyPI license](https://img.shields.io/pypi/l/gestalt-cfg.svg)](https://pypi.python.org/pypi/gestalt-cfg/)

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
3. Config File Directories and Single Config Files
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

Configuration files are supported in JSON and YAML format, with YAML files being given priority over JSON.

Loading a directory of configuration files is done by calling `add_config_path`

```python
g.add_config_path('./testdata')
```

Multiple directory paths can be added:

```python
g.add_config_path('./testdata2')
g.add_config_path('./testdata3')
```

Note that files loaded from a directory are loaded in alphabetical order, with JSON files being loaded first, then YAML files.

Individual files can also be loaded:

```python
g.add_config_file('./testfile.json')
g.add_config_file('./testotherfile.yaml')
```

After all the directory paths and files are added, we can render them:

```python
g.build_config()
```

Note that the the last added directory path takes the most precedence, and will override conflicting keys from previous paths. Individual files take precedence over directories. In addition to this, the rendering flattens the config, for example, the configuration:

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

Nested dictionaries are merged recursively. For example:

```py
# config1.json file contents.
{
  "db": {
    "name": "fake"
  },
  "replicas": 1,
}

# config2.json file contents.
{
  "db": {
    "name": "mydb",
    "password": "password"
  },
}

g.add_config_file('./config1.json')
g.add_config_file('./config2.json')

# Merged result.
{
  "db": {
    "name": "mydb",
    "password": "password"
  },
  "replicas": 1,
}
```

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
6. Dict

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
set_dict(key: str, value: Dict[str, Any]) -> None
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
set_default_dict(key: str, value: Dict[str, Any]) -> None
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

#### Interpolation

Gestalt supports interpolation for the config keys and connect them with the correct provider of the choice.

To use the interpolation, each value needs to have three parts

1. Provider
2. Path
3. Filter

Providers use JSONPath for proper traversal of the secrets and are standard compliant.

The interpolation value needs to be set as follows:

```yaml
key: ref+provider://some-path#filter
```

where `provider`, is the name of the provider, `some-path` is the path for the secret in your provider and `filter` is used to travese the key once fectched that you want to run on the response if the response is a nested object.

The filter is a flattened list with `.` as the generic delimiter in gestalt after flattening.

#### Provider

Gestalt allows third party providers to be used in configuration and fetching respective values as per their system.

Working with providers is extremely simple in Gestalt. All that needs to be done is configuration of the provider and gestalt takes care of the rest.

To configure providers, use the `configure_providers` methods. It takes the `provider_name` and the and instance of the class  which is of type `Provider`.

These should be configured before building the config by calling the method `build_config`.
Eg. The first behaviour is incorrect in case one uses a provider. The second one is correct and recommended

```py
# incorrect way
g.build_config()
g.configure_providers("provider_name", provider)
```

```py
# correct way
g.config_providers("provider_name", provider)
g.build_config()
```

For more information about the each provider configuration, please read the configuration parameters section for the respective provider.

Gestalt supports the following providers

1. Vault

## Vault Provider

Vault Provider is a provider support from gestalt to hashicorp vault.
To instatiate your provider, please use `config_provider` method in gestalt.
Providing the method with a VaultConfig, will configure the provider to connect
with your instance of Vault wherever it is running whether it be local instance
or a cloud instance.

### Configuration Parameters

VaultConfig is a dataclass of type ProviderClass that takes all the vault configuration needed to
connect to the vault instance.

VAULT_ADDR and VAULT_TOKEN are two common environment varibales that are set for working with vault. Hence to work and use the default setup, the Gestalt Vault configuration can read the values from those environment variables on your behalf.

Parameter | Datatype | Default | Required |
---       |   ---    |   ---   | --- |
| role  | string | None | - [x]
| jwt | string | None | - [x]
| url | string | VAULT_ADDR | - [ ]
| token|string|VAULT_TOKEN | - [ ]
| cert | Tuple[string, string] | None | - [ ]
| verify | bool | True | - [ ]

```txt
For kubernetes authentication, one needs to provide `role` and `jwt` as part of the configuration process.
```
