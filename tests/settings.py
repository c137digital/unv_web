SETTINGS = {
    'app': {
        'components': [
            'unv.web',
            'component'
        ],
        'env': 'test'
    },
    'web': {
        'redis': {
            'enabled': False
        }
    },
    'deploy': {
        'components': {
            'web': {
                'static': {
                    'link': False
                }
            }
        }
    }
}
