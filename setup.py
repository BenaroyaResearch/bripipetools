try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'bripipetools',
    'version': '0.3.0',
    'description': 'Software for managing BRI bioinformatics pipelines',
    'author': 'James A. Eddy',
    'author_email': 'james.a.eddy@gmail.com',
    'url': 'https://github.com/jaeddy/bripipetools',
    'license': 'MIT',
    'packages': ['bripipetools'],
    'install_requires': [
        'beautifulsoup4',
        'pymongo',
        'pandas'
    ],
    'setup_requires': ['pytest-runner'],
    'tests_require': ['pytest', 'pytest-cov', 'mock', 'mongomock'],
    'scripts' : [
        'bin/bripipe-dbify',
        'bin/bripipe-postprocess'
    ],
    'zip_safe': False
}

setup(**config)
