from pathlib import Path

from unv.deploy.components.app import AppComponentSettings, AppComponentTasks
from unv.deploy.components.nginx import NginxComponentSettings

from unv.web.settings import SETTINGS


class WebAppComponentSettings(AppComponentSettings):
    NAME = 'web'
    DEFAULT = AppComponentSettings.DEFAULT.update({
        'bin': 'app {settings.port} {instance}',
        'port': 8000,
        'nginx': {'nginx.conf': 'app.conf'}
    })

    @property
    def port(self):
        return self._data['port']

    @property
    def nginx_configs(self):
        for template, path in self._data['nginx_configs'].items():
            if not template.startswith('/'):
                template = (self.local_root / template).resolve()
            yield Path(template), path

    @property
    def domain(self):
        return SETTINGS['domain']

    @property
    def static(self):
        return SETTINGS['static']


class WebComponentTasks(AppComponentTasks):
    SETTINGS = WebAppComponentSettings()
    NAMESPACE = 'web'

    async def sync(self):
        await super().sync()

        nginx = NginxComponentSettings()
        if not nginx.enabled:
            return

        for template, path in self._settings.nginx_configs:
            self._upload_template(
                template, nginx.root / nginx.include.parent / path)
