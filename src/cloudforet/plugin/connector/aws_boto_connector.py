import logging
from typing import List
import boto3

from spaceone.core import utils
from spaceone.core.connector import BaseConnector
from cloudforet.plugin.error.custom import *

__all__ = ['AWSBotoConnector']

_LOGGER = logging.getLogger(__name__)
_DEFAULT_REGION = 'us-east-1'


class AWSBotoConnector(BaseConnector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = None
        self._client = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    def create_session(self, options: dict, secret_data: dict, schema: str):
        self._check_secret_data(secret_data)

        aws_access_key_id = secret_data['aws_access_key_id']
        aws_secret_access_key = secret_data['aws_secret_access_key']
        role_arn = secret_data.get('role_arn')
        external_id = secret_data.get('external_id')

        try:
            if role_arn:
                self._create_session_aws_assume_role(aws_access_key_id, aws_secret_access_key, role_arn, external_id)
            else:
                self._create_session_aws_access_key(aws_access_key_id, aws_secret_access_key)
        except Exception as e:
            raise ERROR_AWS_CONNECTION(reason=e)

        return self.session

    def init_client(self, region_name: str):
        raise NotImplementedError('Method not implemented!')

    def list_regions(self) -> List[str]:
        ec2 = self.session.client('ec2', region_name=_DEFAULT_REGION)
        response = ec2.describe_regions()
        return [region['RegionName'] for region in response['Regions']]

    def get_account_id(self) -> str:
        sts = self.session.client('sts')
        response = sts.get_caller_identity()
        return response.get('Account')

    @staticmethod
    def _check_secret_data(secret_data):
        if 'aws_access_key_id' not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key='secret_data.aws_access_key_id')

        if 'aws_secret_access_key' not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key='secret_data.aws_secret_access_key')

    def _create_session_aws_access_key(self, aws_access_key_id, aws_secret_access_key):
        self.session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key)

        sts = self.session.client('sts')
        sts.get_caller_identity()

    def _create_session_aws_assume_role(self, aws_access_key_id, aws_secret_access_key, role_arn, external_id):
        self._create_session_aws_access_key(aws_access_key_id, aws_secret_access_key)

        sts = self.session.client('sts')

        _assume_role_request = {
            'RoleArn': role_arn,
            'RoleSessionName': utils.generate_id('AssumeRoleSession'),
        }

        if external_id:
            _assume_role_request.update({'ExternalId': external_id})

        assume_role_object = sts.assume_role(**_assume_role_request)
        credentials = assume_role_object['Credentials']

        self.session = boto3.Session(aws_access_key_id=credentials['AccessKeyId'],
                                     aws_secret_access_key=credentials['SecretAccessKey'],
                                     aws_session_token=credentials['SessionToken'])
