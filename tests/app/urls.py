from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from tests.app.viewsets import DelegatedOwnerViewSet
from .viewsets import ContainerViewSet, ItemAViewSet, ItemBViewSet, ItemCViewSet, ItemDViewSet, DenyAllViewSet, \
    AllowOnlyOwnerViewSet

router = DefaultRouter()
router.register(r'container', ContainerViewSet)
router.register(r'item/A', ItemAViewSet)
router.register(r'item/B', ItemBViewSet)
router.register(r'item/C', ItemCViewSet)
router.register(r'item/D', ItemDViewSet)
router.register(r'item/deny', DenyAllViewSet)
router.register(r'item/owner', AllowOnlyOwnerViewSet)
router.register(r'item/AOwner', DelegatedOwnerViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include(router.urls))
]
