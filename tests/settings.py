SETTINGS = {
    'app': {
        'components': [
            'unv.web',
            'component'
        ],
        'env': 'testing'
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
