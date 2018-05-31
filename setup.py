from setuptools import setup

README = """
Delegate django rest framework object permissions to an object pointed by foreign key/m2m

Sample: set up permissions so that anyone having django/django guardian permissions on Invoice will have the same set of permissions on its address:

.. code-block:: python

    class Address(models.Model):
        ... address fields

    class Invoice(models.Model):
        address = models.OneToOneField(Address, related_name='invoice')
        ... invoice fields

    perms = RestPermissions()

    @perms.apply(permissions=DelegatedPermissions(perms, "invoice")
    class AddressViewSet(ModelViewSet):
        queryset = Address.objects.all()
        serializer = AddressSerializer
        ...

    @perms.apply()            # implicitely adds django model permissions and guardian permissions
    class InvoiceViewSet(ModelViewSet):
        queryset = Invoice.objects.all()
        serializer = InvoiceSerializer
        ...
        
See docs and API at `github <https://github.com/mesemus/django-rest-delegated-permissions>`_.
"""


setup(
    name='django-rest-delegated-permissions',
    version='1.0.0',
    packages=[
        'rest_delegated_permissions',
    ],
    description='Taking (delegating) REST permissions from a model instance to a model pointed by ForeignKey/m2m',
    long_description=README,
    author='Mirek Simek',
    author_email='miroslav.simek@gmail.com',
    url='https://github.com/mesemus/django-rest-delegated-permissions',
    license='MIT',
    install_requires=[
        'Django>=1.11',
        'djangorestframework',
        'rest_condition',
        'django-guardian',
    ],
    tests_require=[
        'tox',
        'pytest',
        'pytest-django',
        'pytest_matrix',
        'pytest-runner',
        'pytest-env'
    ],
    extras_require={
        'dev': [
            'sphinx'
        ]
    }
)
