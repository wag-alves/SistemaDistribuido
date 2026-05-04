from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewSet

router = DefaultRouter()
router.register(r'', GameViewSet) # Rota vazia porque o prefixo 'games' virá do Gateway

urlpatterns = [
    path('', include(router.urls)),
]