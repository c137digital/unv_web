from setuptools import setup, find_packages

setup(
    name='unv.web',
    version='0.1.9',
    description="""Web application helpers for unv based on aiohttp""",
    url='http://github.com/c137digital/unv_web',
    author='Morty Space',
    author_email='morty.space@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'unv.app==0.2.3',

        'aiohttp',
        'uvloop',
        'ujson',
        'jinja2'
    ],
    zip_safe=True
)
