# Provider

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
