from pathlib import Path

from unv.utils.tasks import register

from unv.deploy.components.app import AppComponentSettings, AppComponentTasks
from unv.deploy.components.nginx import NginxComponentSettings
from unv.deploy.helpers import get_hosts

from unv.web.settings import SETTINGS

APP_DEFAULT_SETTINGS = AppComponentSettings.DEFAULT.copy()
APP_DEFAULT_SETTINGS.update({
    'systemd': {
        'services': {
            'app.service': {
                'name': 'app_{instance}.service',
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


class WebAppComponentSettings(AppComponentSettings):
    NAME = 'web'
    DEFAULT = APP_DEFAULT_SETTINGS

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
        services = self._data['systemd']['services']
        name = services.keys()[0]
        return services[name]['instances']


class WebAppComponentTasks(AppComponentTasks):
    SETTINGS = WebAppComponentSettings()
    NAMESPACE = 'app'

    def _get_upstream_servers(self):
        for host in get_hosts('app'):
            for instance in range(1, self._settings.instances + 1):
                yield f"{host['private']}:{self._settings.port + instance}"

    @register
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
