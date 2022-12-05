from typing import List
from pydantic import BaseModel
from enum import Enum


class CloudServiceType(BaseModel):
    name: str
    group: str
    provider: str
    is_primary: bool = False
    is_major: bool = False
    metadata: dict
    service_code: str = None
    tags: dict = None
    labels: List[str] = None
