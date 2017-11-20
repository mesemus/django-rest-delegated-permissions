[![Build Status](https://travis-ci.org/mesemus/django-rest-delegated-permissions.svg?branch=master)](https://travis-ci.org/mesemus/django-rest-delegated-permissions)
[![Coverage](https://codecov.io/gh/mesemus/django-rest-delegated-permissions/branch/master/graph/badge.svg)](https://codecov.io/gh/mesemus/django-rest-delegated-permissions)
[![Requirements Status](https://requires.io/github/mesemus/django-rest-delegated-permissions/requirements.svg?branch=master)](https://requires.io/github/mesemus/django-rest-delegated-permissions/requirements/?branch=master)
[![Test report](https://img.shields.io/badge/tests-report-blue.svg)](https://mesemus.github.io/django-rest-delegated-permissions/test_report.html)
[![Coverage report](https://img.shields.io/badge/coverage-report-blue.svg)](https://mesemus.github.io/django-rest-delegated-permissions/htmlcov/index.html)
[![Docs](https://readthedocs.org/projects/pip/badge/)](http://django-rest-delegated-permissions.readthedocs.io/en/latest/)


# django-rest-delegated-permissions
Delegate django rest framework object permissions to an object pointed by foreign key/m2m

Sample: set up permissions so that anyone having django/django guardian permissions on Invoice will have the same set
of permissions on its address:

    class Address(models.Model):
        ... address fields

    class Invoice(models.Model):
        address = models.OneToOneField(Address, related_name='invoice')
        ... invoice fields

    -------------

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
        
See docs and API at http://django-rest-delegated-permissions.readthedocs.io/en/latest/
