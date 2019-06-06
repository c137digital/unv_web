SETTINGS = {
    'app': {
        'components': [
            'unv.web',
            'component'
        ],
        'env': 'test'
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
