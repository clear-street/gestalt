from typing import NamedTuple, TypedDict, Union
import typing

class CACertClient(NamedTuple):
    client_cert_path: str
    client_key_path: str

class HVAC_ClientConfig(TypedDict):
    url: str
    token: str
    cert: Union[None, CACertClient]
    verify: Union[None, bool]

class HVAC_ClientAuthentication(TypedDict):
    role: str
    jwt: str 
