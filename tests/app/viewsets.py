from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer

from rest_delegated_permissions import RestPermissions, DelegatedPermission
from .models import Container, ItemA

# without parameters implicitly adds django model permissions (app_name.view_model, app_name.change_model)
# and support for django-guardian
perms = RestPermissions()

perms.update_permissions({
    # User has permission to Container if he has guardian permissions or django model permissions
    Container: [],

    # User has permission to ItemA if he has guardian or django permissions to the instance or
    # if he has permissions on Container pointed by "parent" field
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
