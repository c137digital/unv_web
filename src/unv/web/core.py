import os
import glob
import pathlib
import asyncio

import uvloop
import aiohttp

from unv.app.helpers import get_app_components

from .settings import SETTINGS


def link_component_static_dirs(component):
    component_path = pathlib.Path(
        os.path.realpath(component.__file__)).parent
    static_path = component_path / 'static'
    public_dir = SETTINGS['web']['static']['paths']['public']
    private_dir = SETTINGS['web']['static']['paths']['private']

    public_app_dirs = str(static_path / public_dir.name / '*')
    for directory in glob.iglob(public_app_dirs):
        os.system('mkdir -p {}'.format(public_dir))
        os.system('ln -sf {} {}'.format(directory, public_dir))

    private_app_dirs = str(static_path / private_dir.name / '*')
    for directory in glob.iglob(private_app_dirs):
        os.system('mkdir -p {}'.format(private_dir))
        os.system('ln -sf {} {}'.format(directory, private_dir))


def create_app():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    app = aiohttp.web.Application(debug=SETTINGS['app']['debug'])

    for component in get_app_components():
        component.setup(app)

    return app
