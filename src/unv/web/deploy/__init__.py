from pathlib import Path

from unv.utils.tasks import register

from unv.deploy.components.app import AppComponentSettings, AppComponentTasks
from unv.deploy.components.nginx import NginxComponentSettings
from unv.deploy.helpers import get_hosts, as_user

from unv.web.settings import SETTINGS

NGINX_SETTINGS = NginxComponentSettings()

APP_DEFAULT_SETTINGS = AppComponentSettings.DEFAULT.copy()
APP_DEFAULT_SETTINGS.update({
    'bin': 'app {instance} {private_ip} {settings.port}',
    'port': 8000,
    'use_https': True,
    'ssl_certificate': 'secure/certs/fullchain.pem',
    'ssl_certificate_key': 'secure/certs/privkey.pem',
    'configs': {'nginx.conf': 'app.conf'},
    'systemd': {
        'services': {
            'app.service': {
                'name': 'app_{instance}.service',
                'boot': True,
                'instances': 1
            }
        }
    },
})


class WebAppComponentSettings(AppComponentSettings):
    NAME = 'app'
    DEFAULT = APP_DEFAULT_SETTINGS

    @property
    def ssl_certificate(self):
        return self.home_abs / self._data['ssl_certificate']

    @property
    def ssl_certificate_key(self):
        return self.home_abs / self._data['ssl_certificate_key']

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
    def domain(self):
        return SETTINGS['domain'].split('//')[1]

    @property
    def instances(self):
        services = self._data['systemd']['services']
        name = list(services.keys())[0]
        return services[name]['instances']

    @property
    def use_https(self):
        return self._data['use_https']


class WebAppComponentTasks(AppComponentTasks):
    SETTINGS = WebAppComponentSettings()
    NAMESPACE = 'app'

    def _get_upstream_servers(self):
        for _, host in get_hosts('app'):
            for instance in range(1, self._settings.instances + 1):
                yield f"{host['private']}:{self._settings.port + instance}"

    @as_user(NGINX_SETTINGS.user)
    async def _upload_nginx_configs(self):
        if not NGINX_SETTINGS.enabled:
            return

        for template, path in self._settings.nginx_configs:
            nginx_path = (
                NGINX_SETTINGS.root / NGINX_SETTINGS.include.parent / path
            )
            await self._upload_template(
                template, nginx_path,
                {
                    'settings': self._settings,
                    'upstream_servers': list(self._get_upstream_servers())
                }
            )

    @register
    async def sync(self):
        await super().sync()
        await self._upload_nginx_configs()
        nginx = NginxComponentSettings()
        print(await self._run('cat {}'.format(nginx.root / nginx.include.parent / 'app.conf')))
