from typing import List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, IPvAnyAddress


class Reference(TypedDict, total=False):
    resource_id: str
    external_link: str


class BaseCloudService(BaseModel):
    name: str = None
    cloud_service_type: str
    cloud_service_group: str
    provider: str
    ip_addresses: Optional[List[IPvAnyAddress]] = []
    account: str = None
    instance_type: str = None
    instance_size: float = 0
    region_code: str = None
    data: dict
    metadata: dict
    reference: Reference = None
    tags: dict = {}
