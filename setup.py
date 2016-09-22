try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'bripipetools',
    'description': 'Software for managing BRI bioinformatics pipelines',
    'author': 'James A. Eddy',
    'author_email': 'james.a.eddy@gmail.com',
    'url': 'https://github.com/jaeddy/bripipetools',
    'license': 'MIT',
    'packages': ['bripipetools'],
    'install_requires': [
        'bs4',
        'pymongo',
        'pandas'
    ],
    'setup_requires': ['pytest-runner'],
    'tests_require': ['pytest', 'mock', 'mongomock'],
    'zip_safe': False
}

setup(**config)
