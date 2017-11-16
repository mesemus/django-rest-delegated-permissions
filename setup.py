import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='django-rest-delegated-permissions',
    version='0.1',
    packages=['rest_delegated_permissions'],
    description='Taking (delegating) REST permissions from a model instance to a model pointed by ForeignKey/m2m',
    long_description=README,
    author='Mirek Simek',
    author_email='miroslav.simek@gmail.com',
    url='https://github.com/mesemus/django-rest-delegated-permissions',
    license='MIT',
    install_requires=[
        'Django>=1.10',
        'djangorestframework',
        'rest_condition',
        'django-guardian',
        'pytest-runner',
        'pytest-env'
    ],
    tests_require=[
        'tox',
        'pytest',
        'pytest-django',
        'pytest_matrix'
    ]
)
