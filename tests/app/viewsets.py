from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from rest_delegated_permissions import RestPermissions, DelegatedPermission
from .models import Container, ItemA, ItemB, ItemC, ItemD

# without parameters implicitly adds django model permissions (app_name.view_model, app_name.change_model)
# and support for django-guardian
perms = RestPermissions()

#
# can set the permission either here or on a perms.apply() call - see itemB, C, D.
# In that case it takes the model class from the queryset field defined on the viewset
#
perms.update_permissions({
    # User has permission to Container if he has guardian permissions or django model permissions
    Container: [],

    # User has permission to ItemA if he has guardian or django permissions to the instance or
    # if he has permission to Container pointed by "parent" field
    ItemA: DelegatedPermission(perms, 'parent'),
})


class ContainerSerializer(ModelSerializer):
    class Meta:
        model = Container
        exclude = ()


@perms.apply()
class ContainerViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list` and `detail` actions.
    """
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer


class ItemASerializer(ModelSerializer):
    class Meta:
        model = ItemA
        exclude = ()


@perms.apply()
class ItemAViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list` and `detail` actions.
    """
    queryset = ItemA.objects.all()
    serializer_class = ItemASerializer


class ItemBSerializer(ModelSerializer):
    class Meta:
        model = ItemB
        exclude = ()


# User has permission to ItemB if he has guardian or django permissions to the instance or
# if he has permission to any of Containers pointed by "parents" m2m field
@perms.apply(permissions=DelegatedPermission(perms, 'parents'))
class ItemBViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list` and `detail` actions.
    """
    queryset = ItemB.objects.all()
    serializer_class = ItemBSerializer


class ItemCSerializer(ModelSerializer):
    class Meta:
        model = ItemC
        exclude = ()

# User has permission to ItemC if he has guardian or django permissions to the instance or
# if he has permission to any of Containers that point to it via its item_c ForeignKey.
# Note: we are checking perms for ItemC and the Foreign Key is defined on Container,
# so we need to put in the related_name
@perms.apply(permissions=DelegatedPermission(perms, 'container'))
class ItemCViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list` and `detail` actions.
    """
    queryset = ItemC.objects.all()
    serializer_class = ItemCSerializer


class ItemDSerializer(ModelSerializer):
    class Meta:
        model = ItemD
        exclude = ()


# User has permission to ItemD if he has guardian or django permissions to the instance or
# if he has permission to any of Containers that point to it via its items_d m2m field
# Note: we are checking perms for ItemD and the m2m field is defined on Container,
# so we need to put in the related_name
@perms.apply(permissions=DelegatedPermission(perms, 'containers'))
class ItemDViewSet(viewsets.ModelViewSet):
    """
    This view set automatically provides `list` and `detail` actions.
    """
    queryset = ItemD.objects.all()
    serializer_class = ItemDSerializer
