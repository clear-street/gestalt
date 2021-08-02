# Provider

Gestalt allows third party providers to be used in configuration and fetching respective values as per their system.

Working with providers is extremely simple in Gestalt. All that needs to be done is configuration of the provider and gestalt takes care of the rest.

To configure providers, use the `configure_providers` methods. It takes the `provider_name` and the config which is of type `ProviderConfig`.

These should be configured before building the config from the method `build_config`

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

Parameter | Datatype | Default |
---       |   ---    |   ---   |
| role  | string | None |
| jwt | string | None
| url | string | VAULT_ADDR
| token|string|VAULT_TOKEN
| cert | Tuple[string, string] | None
| verify | bool | True

```txt
For kubernetes authentication, one needs to provide role and jwt as part of the configuration process.
```
