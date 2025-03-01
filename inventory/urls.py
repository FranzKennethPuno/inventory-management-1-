# inventory/urls.py
# inventory/urls.py (add this import)
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUserView
from .views import LogoutView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PantryItemViewSet, RecipeViewSet, NotificationView, BarcodeScanView, RecipeUsageView,
    MealPlanViewSet, UserPreferenceViewSet, AnalyticsView, UsageAnalyticsView, CommunityPostViewSet
)

router = DefaultRouter()
router.register(r'inventory/items', PantryItemViewSet, basename='pantryitem')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'inventory/meal-plans', MealPlanViewSet, basename='mealplan')
router.register(r'inventory/community/posts', CommunityPostViewSet, basename='communitypost')

urlpatterns = [
    path('', include(router.urls)),
    path('inventory/notifications/', NotificationView.as_view(), name='notifications'),
    path('inventory/scan/', BarcodeScanView.as_view(), name='barcode-scan'),
    path('inventory/recipes/used/', RecipeUsageView.as_view(), name='recipe-usage'),
    path('inventory/analytics/spending/', AnalyticsView.as_view(), name='analytics-spending'),
    path('inventory/analytics/usage/', UsageAnalyticsView.as_view(), name='analytics-usage'),
    # User preferences and history endpoints:
    path('inventory/users/<int:user_id>/preferences/', UserPreferenceViewSet.as_view({'get': 'retrieve_preferences'}), name='user-preferences'),
    path('inventory/users/<int:user_id>/history/', UserPreferenceViewSet.as_view({'get': 'list_history'}), name='user-history'),
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', obtain_auth_token, name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout')
]
