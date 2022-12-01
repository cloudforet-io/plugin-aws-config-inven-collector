import logging

from spaceone.core.manager import BaseManager
from cloudforet.plugin.model.collector_model import PluginMetadata
from cloudforet.plugin.connector.aws_boto_connector import AWSBotoConnector

_LOGGER = logging.getLogger(__name__)


class CollectorManager(BaseManager):

    @staticmethod
    def init_response(options):
        plugin_metadata = PluginMetadata()

        return {
            'metadata': plugin_metadata.dict()
        }

    def verify_plugin(self, options, secret_data, schema):
        aws_connector: AWSBotoConnector = self.locator.get_connector('AWSBotoConnector')
        aws_connector.create_session(options, secret_data, schema)
