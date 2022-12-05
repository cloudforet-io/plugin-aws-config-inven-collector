import logging
from typing import List, Generator

from spaceone.core.error import *
from spaceone.core.manager import BaseManager
from cloudforet.plugin.model.plugin_info_model import PluginInfo, ResourceType
from cloudforet.plugin.model.resource_info_model import ResourceInfo, State
from cloudforet.plugin.connector.aws_boto_connector import AWSBotoConnector

_LOGGER = logging.getLogger(__name__)
_PLUGIN_METADATA = {
    'supported_resource_type': [
        ResourceType.cloud_service,
        ResourceType.cloud_service_type,
        ResourceType.cloud_service
    ]
}


class CollectorManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aws_connector: AWSBotoConnector = self.locator.get_connector(AWSBotoConnector)
        self.provider = 'aws'
        self.cloud_service_group = None
        self.cloud_service_type = None
        self.region_name = None

    @staticmethod
    def init_response(options: dict) -> dict:
        response = PluginInfo(metadata=_PLUGIN_METADATA)
        return response.dict()

    def create_session(self, options: dict, secret_data: dict, schema: str) -> object:
        return self.aws_connector.create_session(options, secret_data, schema)

    def list_regions(self) -> List[str]:
        return self.aws_connector.list_regions()

    def collect(self, options: dict, region_name: str) -> Generator[dict, None, None]:
        raise NotImplementedError('Method not implemented!')

    def make_response(self, resource_data, resource_type: str = 'inventory.CloudService') -> dict:
        return self.validate_response({
            'state': State.success,
            'resource_type': resource_type,
            'resource': resource_data
        })

    def error_response(self, error: Exception) -> dict:
        if not isinstance(error, ERROR_BASE):
            error = ERROR_UNKNOWN(message=error)

        _LOGGER.error(f'[error_response] ({self.region_name}) {error.error_code}: {error.message}', exc_info=True)
        return self.validate_response({
            'state': State.failre,
            'message': error.message,
            'resource_type': ResourceType.error,
            'resource': {
                'provider': self.provider,
                'cloud_service_group': self.cloud_service_group,
                'cloud_service_type': self.cloud_service_type
            }
        })

    @staticmethod
    def validate_response(resource_data):
        response = ResourceInfo(**resource_data)
        return response.dict()
