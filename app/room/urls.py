from django.urls import (path, include)
from rest_framework.routers import DefaultRouter
from room import views

router = DefaultRouter()
router.register('rooms', views.RoomViewSet)
app_name = 'room'

urlpatterns = [
    path('', include(router.urls))
]
