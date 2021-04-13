from typing import Tuple, TypedDict, Union

class HVAC_ClientConfig(TypedDict):
    url: str
    token: str
    cert: Union[None, Tuple]
    verify: Union[None, bool]

class HVAC_ClientAuthentication(TypedDict):
    role: str
    jwt: str 