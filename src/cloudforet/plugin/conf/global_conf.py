LOG = {
    'filters': {
        'masking': {
            'rules': {
                'Collector.verify': [
                    'secret_data'
                ],
                'Collector.collect': [
                    'secret_data'
                ]
            }
        }
    }
}
