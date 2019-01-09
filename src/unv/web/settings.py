from unv.app.core import create_component_settings, get_project_root

PROJECT_ROOT = get_project_root()

PUBLIC_PRIVATE_FILES_AND_URLS_SCHEMA = {
    "type": "object",
    "properties": {
        "paths": {
            "type": "object",
            "properties": {
                "public": {"type": "string", "required": True},
                "private": {"type": "string", "required": True}
            }
        },
        "urls": {
            "type": "object",
            "properties": {
                "public": {"type": "string", "required": True},
                "private": {"type": "string", "required": True}
            }
        }
    }
}

SCHEMA = {
    "type": "object",
    "properties": {
        "domain": {
            "type": "string",
            "required": "true"
        },
        "protocol": {
            "type": "string",
            "allowed": ["http", "https"],
            "required": "true"
        },
        "host": {
            "type": "string",
            "required": "true"
        },
        "port": {
            "type": "integer",
            "required": "true"
        },
        "autoreload": {
            "type": "boolean",
            "required": "true"
        },
        "static": PUBLIC_PRIVATE_FILES_AND_URLS_SCHEMA,
        "media": PUBLIC_PRIVATE_FILES_AND_URLS_SCHEMA
    }
}

DEFAULTS = {
    'domain': 'app.local',
    'protocol': 'https',
    'host': '0.0.0.0',
    'port': '8{:03d}',
    'autoreload': False,
    'static': {
        'paths': {
            'public': PROJECT_ROOT / 'static' / 'public',
            'private': PROJECT_ROOT / 'static' / 'private'
        },
        'urls': {
            'public': '/static/public',
            'private': '/static/private'
        }
    },
    'media': {
        'paths': {
            'public': PROJECT_ROOT / 'media' / 'public',
            'private': PROJECT_ROOT / 'media' / 'private'
        },
        'urls': {
            'public': '/media/public',
            'private': '/media/private'
        }
    }
}

SETTINGS = create_component_settings('web', DEFAULTS, SCHEMA)
