from django.contrib.auth.models import User
from django.db import models


#
# Models for tests
#


class Container(models.Model):
    name    = models.CharField(max_length=10)
    item_c  = models.ForeignKey('ItemC', null=True, blank=True, related_name='container', on_delete=models.CASCADE)
    items_d = models.ManyToManyField('ItemD', related_name='containers')
    # owner for some of the tests
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ('view_container', 'View all containers'),
        )


class ItemA(models.Model):
    name   = models.CharField(max_length=10)
    parent = models.ForeignKey(Container, on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ('view_itema', 'View Item A'),
        )


class ItemB(models.Model):
    name    = models.CharField(max_length=10)
    parents = models.ManyToManyField(Container)

    class Meta:
        permissions = (
            ('view_itemb', 'View Item B'),
        )


class ItemC(models.Model):
    name    = models.CharField(max_length=10)

    class Meta:
        permissions = (
            ('view_itemc', 'View Item C'),
        )


class ItemD(models.Model):
    name    = models.CharField(max_length=10)

    class Meta:
        permissions = (
            ('view_itemd', 'View Item D'),
        )


class ItemE(models.Model):
    name   = models.CharField(max_length=10)
    parent = models.ForeignKey(Container, on_delete=models.CASCADE)
    owner  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        permissions = (
            ('view_iteme', 'View Item E'),
        )
