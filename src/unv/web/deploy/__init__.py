from pathlib import Path

from unv.utils.tasks import register

from unv.deploy.tasks import DeployComponentTasksBase
from unv.deploy.components.systemd import SystemdTasksMixin
from unv.deploy.components.nginx import NginxComponentSettings
from unv.deploy.helpers import get_hosts, as_user, ComponentSettingsBase

from unv.web.settings import SETTINGS

NGINX_SETTINGS = NginxComponentSettings()


class WebAppComponentSettings(ComponentSettingsBase):
    NAME = 'web'
    DEFAULT = {
        'bin': 'web {instance} {private_ip} {settings.port}',
        'port': 8000,
        'use_https': True,
        'ssl_certificate': 'secure/certs/fullchain.pem',
        'ssl_certificate_key': 'secure/certs/privkey.pem',
        'configs': {'nginx.conf': 'web.conf'},
        'systemd': {
            'template': 'web.service',
            'name': 'web_{instance}.service',
            'boot': True,
            'instances': {'count': 1}
        },
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
        return SETTINGS['domain'].split('//')[1]

    @property
    def use_https(self):
        return self._data['use_https']


class WebAppComponentTasks(DeployComponentTasksBase, SystemdTasksMixin):
    SETTINGS = WebAppComponentSettings()
    NAMESPACE = 'web'

    def _get_upstream_servers(self):
        for _, host in get_hosts('app'):
            with self._set_host(host):
                count = await self._get_systemd_instances_count()
            for instance in range(1, count + 1):
                yield f"{host['private']}:{self._settings.port + instance}"

    @register
    async def sync(self):
        name = (await self._local('python setup.py --name')).strip()
        version = (await self._local('python setup.py --version')).strip()
        package = f'{name}-{version}.tar.gz'

        await self._local('pip install -e .')
        await self._local('python setup.py sdist bdist_wheel')
        await self._upload(Path('dist', package))
        await self._local('rm -rf ./build ./dist')
        await self._python.pip(f'install -I {package}')
        await self._rmrf(Path(package))
        await self._upload(Path('secure'))
        await self._sync_systemd_units()

        nginx = NginxComponentSettings()

        if not nginx.enabled:
            return

        for template, path in self._settings.nginx_configs:
            with self._set_user(nginx.user):
                await self._upload_template(
                    template,  nginx.root / nginx.include.parent / path,
                    {
                        'settings': self._settings,
                        'upstream_servers': list(self._get_upstream_servers())
                    }
                )
        print(await self._run('cat {}'.format(nginx.root / nginx.include.parent / 'app.conf')))
