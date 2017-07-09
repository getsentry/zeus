from setuptools import setup, find_packages

install_requires = [
    'blinker==1.4',
    'cached-property==1.3.0',
    'celery==4.0.2',
    'flask==0.12.2',
    'flask-alembic==2.0.1',
    'flask-sqlalchemy==2.2',
    'honcho==1.0.1',
    'lxml==3.8.0',
    'marshmallow==2.13.5',
    'oauth2client==4.1.2',
    'psycopg2==2.7.1',
    'raven==6.1.0',
    'redis==2.10.5',
    'requests==2.18.1',
    'unidecode==0.04.21',
]

dev_requires = [
    'flake8==3.3.0',
    'ipython==6.1.0',
    'yapf==0.16.2',
]

test_requires = [
    'exam==0.10.6',
    'factory_boy==2.8.1',
    'pytest==3.1.2',
    'pytest-cov==2.5.1',
    'pytest-mock==1.6.0',
    'pytest-responses==0.1.0',
    'pytest-xdist==1.18.0',
]

setup(
    name='zeus',
    version='0.1.0',
    packages=find_packages(),
    license='Apache 2.0',
    entry_points={
        'console_scripts': ['zeus=zeus.cli:main'],
    },
    long_description=open('README.md').read(),
    install_requires=install_requires + dev_requires + test_requires,
)
