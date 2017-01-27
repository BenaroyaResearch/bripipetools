try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'bripipetools',
    'version': '0.4.0',
    'description': 'Software for managing BRI bioinformatics pipelines',
    'author': 'James A. Eddy',
    'author_email': 'james.a.eddy@gmail.com',
    'url': 'https://github.com/jaeddy/bripipetools',
    'license': 'MIT',
    'packages': ['bripipetools'],
    'package_data': {
        'bripipetools': [
            'config/default.ini',
            'config/logging_config.ini',
            'data/*'
        ]
    },
    'install_requires': [
        'Click',
        'beautifulsoup4',
        'pymongo',
        'pandas'
    ],
    'entry_points': {
        'console_scripts': 'bripipetools = bripipetools.__main__:main'
    },
    'setup_requires': ['pytest-runner'],
    'tests_require': ['pytest', 'pytest-cov', 'mock', 'mongomock'],
    'zip_safe': False
}

setup(**config)
