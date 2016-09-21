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
    'zip_safe': False
}

setup(**config)
