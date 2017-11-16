from django.db import models


#
# Models for tests
#


class Container(models.Model):
    name    = models.CharField(max_length=10)
    item_c  = models.ForeignKey('ItemC', null=True, blank=True)
    items_d = models.ManyToManyField('ItemD')

    class Meta:
        permissions = (
            ('view_container', 'View all containers'),
        )


class ItemA(models.Model):
    name   = models.CharField(max_length=10)
    parent = models.ForeignKey(Container)


class ItemB(models.Model):
    name    = models.CharField(max_length=10)
    parents = models.ManyToManyField(Container)


class ItemC(models.Model):
    name    = models.CharField(max_length=10)


class ItemD(models.Model):
    name    = models.CharField(max_length=10)
