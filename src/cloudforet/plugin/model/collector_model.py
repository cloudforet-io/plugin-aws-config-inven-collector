from typing import Dict
from pydantic import BaseModel

__all__ = ['PluginMetadata']


class PluginMetadata(BaseModel):
    metadata: Dict = {}

