from pathlib import Path

from unv.utils.tasks import register

from unv.deploy.components.app import AppComponentTasks, AppComponentSettings
from unv.deploy.components.nginx import NginxComponentSettings
from unv.deploy.helpers import get_hosts


class WebAppComponentSettings(AppComponentSettings):
    NAME = 'app'
    DEFAULT = {
        'bin': 'app',
        'settings': 'secure.production',
        'instance': 1,
        'host': '0.0.0.0',
        'port': 8000,
        'domain': 'app.local',
        'use_https': True,
        'ssl_certificate': 'secure/certs/fullchain.pem',
        'ssl_certificate_key': 'secure/certs/privkey.pem',
        'watch': {
            'dir': './src',
            'exclude': ['__pycache__']
        },
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
                'dir': 'static/public'
            },
            'private': {
                'url': '/static/private',
                'dir': 'static/private'
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
    def host(self):
        return self._data['host']

    @property
    def port(self):
        return self._data['port']

    @property
    def nginx_config(self):
        nginx = self._data['nginx']
        template, path = nginx['template'], nginx['name']
        if not template.startswith('/'):
            template = (self.local_root / template).resolve()
        return Path(template), path

    @property
    def domain(self):
        return self._data['domain']

    @property
    def static_public_dir(self):
        return self.home_abs / Path(self._data['static']['public']['dir'])

    @property
    def static_private_dir(self):
        return self.home_abs / Path(self._data['static']['private']['dir'])

    @property
    def static_public_url(self):
        return self._data['static']['public']['url']

    @property
    def static_private_url(self):
        return self._data['static']['private']['url']

    @property
    def use_https(self):
        return self._data['use_https']


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
        template, path = self._settings.nginx_config
        with self._set_user(nginx.user):
            await self._upload_template(
                template,  nginx.root / nginx.include.parent / path,
                {'settings': self._settings, 'upstream_servers': servers}
            )

    @register
    async def sync(self):
        await super().sync()
        await self._sync_nginx_configs()
