try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'bripipetools',
    'version': '0.3.4',
    'description': 'Software for managing BRI bioinformatics pipelines',
    'author': 'James A. Eddy',
    'author_email': 'james.a.eddy@gmail.com',
    'url': 'https://github.com/jaeddy/bripipetools',
    'license': 'MIT',
    'packages': ['bripipetools'],
    'package_data': {
        'bripipetools': ['config/default.ini', 'data/*']
    },
    'install_requires': [
        'Click',
        'beautifulsoup4',
        'pymongo',
        'pandas'
    ],
    'entry_points': {
        'console_scripts': 'bripipetools = bripipetools.__main__:cli'
    },
    'setup_requires': ['pytest-runner'],
    'tests_require': ['pytest', 'pytest-cov', 'mock', 'mongomock'],
    'scripts': [
        'bin/bripipe-dbify',
        'bin/bripipe-postprocess',
        'bin/bripipe-wrapup',
    ],
    'zip_safe': False
}

setup(**config)
