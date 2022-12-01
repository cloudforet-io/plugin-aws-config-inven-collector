import logging

from cloudforet.plugin.connector.aws_boto_connector import AWSBotoConnector

__all__ = ['AWSConfigServiceConnector']

_LOGGER = logging.getLogger(__name__)


class AWSConfigServiceConnector(AWSBotoConnector):
    pass