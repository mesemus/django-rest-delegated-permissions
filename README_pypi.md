Delegate django rest framework object permissions to an object pointed by foreign key/m2m

Sample: set up permissions so that anyone having django/django guardian permissions on Invoice will have the same set of permissions on its address:

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
        
See docs and API at https://github.com/mesemus/django-rest-delegated-permissions
