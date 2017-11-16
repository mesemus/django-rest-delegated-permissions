from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from .viewsets import ContainerViewSet, ItemAViewSet

router = DefaultRouter()
router.register(r'container', ContainerViewSet)
router.register(r'item/A', ItemAViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include(router.urls))
]
