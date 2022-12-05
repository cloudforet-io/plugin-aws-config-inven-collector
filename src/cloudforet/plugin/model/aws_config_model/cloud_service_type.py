from typing import List
from cloudforet.plugin.model.cloud_service_type_model import BaseCloudServiceType

_METADATA = {
    'view': {
        'search': [
            {
                'key': 'data.arn',
                'name': 'ARN'
            },
            {
                'key': 'data.status',
                'name': 'Status'
            },
            {
                'key': 'data.compliance.compliance_type',
                'name': 'Compliance'
            }
        ],
        'table': {
            'layout': {
                'name': '',
                'type': 'query-search-table',
                'options': {
                    'fields': [
                        {
                            'type': 'enum',
                            'name': 'Status',
                            'key': 'data.status',
                            'options': {
                                'FAILED': {
                                    'type': 'badge',
                                    'options': {
                                        'background_color': 'coral.500'
                                    }
                                },
                                'PASS': {
                                    'type': 'badge',
                                    'options': {
                                        'background_color': 'indigo.500'
                                    }
                                }
                            }
                        },
                        {
                            'type': 'text',
                            'key': 'data.source.owner_display',
                            'name': 'Type'
                        },
                        {
                            'type': 'integer',
                            'key': 'data.failed_resource_count',
                            'name': 'Failed Resources'
                        }
                    ]
                }
            }
        },
        'widget': [
            {
                'name': 'Total Count',
                'type': 'summary',
                'options': {
                    'value_options': {
                        'key': 'value',
                        'options': {
                            'default': 0
                        }
                    }
                },
                'query': {
                    'aggregate': [
                        {
                            'count': {
                                'name': 'value'
                            }
                        }
                    ],
                    'filter': [
                        {'key': 'provider', 'value': 'aws', 'operator': 'eq'},
                        {'key': 'cloud_service_group', 'value': 'Compliance', 'operator': 'eq'},
                        {'key': 'cloud_service_type', 'value': 'CIS-AWS-1.4', 'operator': 'eq'},
                    ]
                }
            },
            {
                'name': 'Failed Count',
                'type': 'summary',
                'options': {
                    'value_options': {
                        'key': 'value',
                        'options': {
                            'default': 0
                        }
                    }
                },
                'query': {
                    'aggregate': [
                        {
                            'count': {
                                'name': 'value'
                            }
                        }
                    ],
                    'filter': [
                        {'key': 'data.status', 'value': 'FAILED', 'operator': 'eq'},
                        {'key': 'provider', 'value': 'aws', 'operator': 'eq'},
                        {'key': 'cloud_service_group', 'value': 'Compliance', 'operator': 'eq'},
                        {'key': 'cloud_service_type', 'value': 'CIS-AWS-1.4', 'operator': 'eq'},
                    ]
                }
            },
        ]
    }
}


class CloudServiceType(BaseCloudServiceType):
    name: str = 'CIS-AWS-1.4'
    group: str = 'Compliance'
    provider: str = 'aws'
    is_primary: bool = True
    is_major: bool = True
    metadata: dict = _METADATA
    labels: List[str] = ['Security']
    tags: dict = {
        'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/aws/AWS-Config.svg',
        'spaceone:display_name': 'CIS AWS v1.4'
    }
