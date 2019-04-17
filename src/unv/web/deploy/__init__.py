from pathlib import Path

from unv.deploy.components.app import AppComponentSettings, AppComponentTasks
from unv.deploy.components.nginx import NginxComponentSettings
from unv.deploy.helpers import get_hosts

from unv.web.settings import SETTINGS


class WebAppComponentSettings(AppComponentSettings):
    NAME = 'web'
    DEFAULT = AppComponentSettings.DEFAULT.update({
        'systemd': {
            'services': {
                'web.service': {
                    'name': 'web_{instance}.service',
                    'boot': True,
                    'instances': 1
                }
            }
        },
        'use_https': True,
        'ssl_certificate': 'secure/certs/fullchain.pem',
        'ssl_certificate_key': 'secure/certs/privkey.pem',
        'configs': {
            'nginx.conf': 'app.conf'
        }
    })

    @property
    def ssl_certificate(self):
        return self._data['ssl_certificate']

    @property
    def ssl_certificate_key(self):
        return self._data['ssl_certificate_key']

    @property
    def port(self):
        return self._data['port']

    @property
    def nginx_configs(self):
        for template, path in self._data['configs'].items():
            if not template.startswith('/'):
                template = (self.local_root / template).resolve()
            yield Path(template), path

    @property
    def web(self):
        return SETTINGS

    @property
    def instances(self):
        return self._data['systemd']['services']['web.service']['instances']


class WebComponentTasks(AppComponentTasks):
    SETTINGS = WebAppComponentSettings()
    NAMESPACE = 'web'

    async def _get_upstream_servers(self):
        for host in get_hosts('web'):
            for instance in range(1, self._settings.instances + 1):
                yield f"{host['private']}:{self._settings.port + instance}"

    async def sync(self):
        await super().sync()

        nginx = NginxComponentSettings()
        if not nginx.enabled:
            return

        for template, path in self._settings.nginx_configs:
            self._upload_template(
                template, nginx.root / nginx.include.parent / path,
                {'upstream_servers': list(self._get_upstream_servers())}
            )
