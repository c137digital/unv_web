from pathlib import Path

from unv.utils.tasks import register

from unv.deploy.components.app import AppComponentTasks, AppComponentSettings
from unv.deploy.components.nginx import NginxComponentSettings
from unv.deploy.helpers import get_hosts

from unv.web.settings import SETTINGS


class WebAppComponentSettings(AppComponentSettings):
    NAME = 'app'
    DEFAULT = {
        'bin': 'app',
        'settings': 'secure.production',
        'instance': 1,
        'host': '0.0.0.0',
        'port': 8000,
        'use_https': True,
        'ssl_certificate': 'secure/certs/fullchain.pem',
        'ssl_certificate_key': 'secure/certs/privkey.pem',
        'nginx': {
            'template': 'nginx.conf',
            'name': 'web.conf'
        },
        'systemd': {
            'template': 'web.service',
            'name': 'web_{instance}.service',
            'boot': True,
            'instances': {'count': 1}
        },
        'static': {
            'public': {
                'url': '/static/public',
                'path': 'static/public'
            },
            'private': {
                'url': '/static/private',
                'path': 'static/private'
            }
        }
    }

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
    def domain(self):
        return SETTINGS['domain']

    @property
    def use_https(self):
        return self._data['use_https']

    # TODO: move to static settings base
    @property
    def web(self):
        return SETTINGS


DEPLOY_SETTINGS = WebAppComponentSettings()


class WebAppComponentTasks(AppComponentTasks):
    SETTINGS = DEPLOY_SETTINGS
    NAMESPACE = 'app'

    async def _get_upstream_servers(self):
        for _, host in get_hosts('app'):
            with self._set_host(host):
                count = await self._get_systemd_instances_count()
            for instance in range(1, count + 1):
                yield f"{host['private']}:{self._settings.port + instance}"

    async def _sync_nginx_configs(self):
        nginx = NginxComponentSettings()
        if not nginx.enabled:
            return

        servers = [server async for server in self._get_upstream_servers()]
        for template, path in self._settings.nginx_configs:
            with self._set_user(nginx.user):
                await self._upload_template(
                    template,  nginx.root / nginx.include.parent / path,
                    {'settings': self._settings, 'upstream_servers': servers}
                )

    @register
    async def sync(self):
        await super().sync()
        await self._sync_nginx_configs()
