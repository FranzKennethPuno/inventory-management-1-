# inventory/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from django.contrib.auth.models import User
from .models import PantryItem, Recipe, MealPlan, UserPreference, InventoryHistory, CommunityPost, Comment
from .serializers import (
    PantryItemSerializer, RecipeSerializer, MealPlanSerializer,
    UserPreferenceSerializer, InventoryHistorySerializer, CommunityPostSerializer, CommentSerializer
)

# 1. PantryItemViewSet for inventory items endpoints:
class PantryItemViewSet(viewsets.ModelViewSet):
    queryset = PantryItem.objects.all()
    serializer_class = PantryItemSerializer

    # GET /inventory/items/low-stock
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        items = PantryItem.objects.filter(quantity__lt=F('threshold'))
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    # PUT /inventory/items/{itemId}/update
    @action(detail=True, methods=['put'], url_path='update')
    def update_quantity(self, request, pk=None):
        item = self.get_object()
        new_qty = request.data.get('quantity')
        if new_qty is not None:
            item.quantity = new_qty
            item.save()
            return Response(self.get_serializer(item).data)
        return Response({'error': 'Quantity not provided'}, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /inventory/items/{itemId}/remove
    @action(detail=True, methods=['delete'], url_path='remove')
    def remove_item(self, request, pk=None):
        item = self.get_object()
        item.delete()
        return Response({'message': 'Item removed successfully'}, status=status.HTTP_204_NO_CONTENT)

# 2. RecipeViewSet for recipe-related endpoints:
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    # GET /recipes/suggest
    @action(detail=False, methods=['get'], url_path='suggest')
    def suggest(self, request):
        # Dummy logic: return first 5 recipes
        recipes = Recipe.objects.all()[:5]
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    # GET /recipes/{recipeId}/details
    @action(detail=True, methods=['get'], url_path='details')
    def details(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    # GET /recipes/popular
    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request):
        recipes = Recipe.objects.order_by('-popularity')[:5]
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    # GET /recipes/{recipeId}/nutrition
    @action(detail=True, methods=['get'], url_path='nutrition')
    def nutrition(self, request, pk=None):
        recipe = self.get_object()
        # Dummy nutritional info
        nutrition_info = {
            'calories': 500,
            'protein': '25g',
            'carbs': '60g',
            'fats': '20g'
        }
        return Response(nutrition_info)

    # GET /inventory/recipes/{recipeId}/substitutions
    @action(detail=True, methods=['get'], url_path='substitutions')
    def substitutions(self, request, pk=None):
        recipe = self.get_object()
        # Dummy substitutions mapping
        substitutions = {
            'sugar': 'honey',
            'butter': 'olive oil'
        }
        return Response({'recipe': recipe.name, 'substitutions': substitutions})

# 3. Notification endpoint: GET /inventory/notifications
class NotificationView(APIView):
    def get(self, request):
        # Dummy notifications
        notifications = [
            {'message': 'Milk is running low', 'item': 'Milk'},
            {'message': 'Eggs will expire soon', 'item': 'Eggs'},
        ]
        return Response(notifications)

# 4. Barcode scan endpoint: POST /inventory/scan
class BarcodeScanView(APIView):
    def post(self, request):
        barcode = request.data.get('barcode')
        if not barcode:
            return Response({'error': 'Barcode not provided'}, status=status.HTTP_400_BAD_REQUEST)
        # Simulated scan result
        dummy_item = {
            'name': 'Scanned Item',
            'quantity': 1,
            'expiration_date': None,
            'threshold': 1
        }
        return Response(dummy_item)

# 5. Recipe usage endpoint: POST /inventory/recipes/used
class RecipeUsageView(APIView):
    def post(self, request):
        recipe_id = request.data.get('recipe_id')
        user_id = request.data.get('user_id')
        try:
            # Dummy logic: update by selecting the first pantry item
            item = PantryItem.objects.first()
            user = User.objects.get(pk=user_id)
        except (PantryItem.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'Invalid recipe or user'}, status=status.HTTP_400_BAD_REQUEST)
        history = InventoryHistory.objects.create(user=user, item=item, action='used')
        from .serializers import InventoryHistorySerializer
        serializer = InventoryHistorySerializer(history)
        return Response(serializer.data)

# 6. MealPlanViewSet for meal plan endpoints:
class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer

    # POST /inventory/meal-plans/generate
    @action(detail=False, methods=['post'], url_path='generate')
    def generate_meal_plan(self, request):
        user_id = request.data.get('user_id')
        plan_name = request.data.get('plan_name', 'Weekly Meal Plan')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        meal_plan = MealPlan.objects.create(user=user, plan_name=plan_name, summary="Dummy meal plan summary.")
        serializer = self.get_serializer(meal_plan)
        return Response(serializer.data)

    # GET /inventory/meal-plans/{planId}/summary
    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        meal_plan = self.get_object()
        return Response({'plan_name': meal_plan.plan_name, 'summary': meal_plan.summary})

# 7. User Preferences and Inventory History endpoints:
from rest_framework.viewsets import ViewSet
class UserPreferenceViewSet(ViewSet):
    # GET /inventory/users/{userId}/preferences
    def retrieve_preferences(self, request, user_id=None):
        try:
            pref = UserPreference.objects.get(user__id=user_id)
            serializer = UserPreferenceSerializer(pref)
            return Response(serializer.data)
        except UserPreference.DoesNotExist:
            return Response({'error': 'Preferences not found'}, status=status.HTTP_404_NOT_FOUND)

    # GET /inventory/users/{userId}/history
    def list_history(self, request, user_id=None):
        histories = InventoryHistory.objects.filter(user__id=user_id)
        serializer = InventoryHistorySerializer(histories, many=True)
        return Response(serializer.data)

# 8. Analytics endpoints:
class AnalyticsView(APIView):
    # GET /inventory/analytics/spending
    def get(self, request, format=None):
        spending_data = {
            'total_spent': 250.00,
            'monthly_average': 50.00
        }
        return Response({'spending': spending_data})

class UsageAnalyticsView(APIView):
    # GET /inventory/analytics/usage
    def get(self, request, format=None):
        usage_data = {
            'most_used_item': 'Milk',
            'usage_pattern': 'Weekly'
        }
        return Response({'usage': usage_data})

# 9. Community Posts endpoints:
class CommunityPostViewSet(viewsets.ModelViewSet):
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer

    # GET /inventory/community/posts/trending
    @action(detail=False, methods=['get'], url_path='trending')
    def trending(self, request):
        posts = CommunityPost.objects.order_by('-trending_score')[:5]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    # GET /inventory/community/posts/{postId}/comments
    @action(detail=True, methods=['get'], url_path='comments')
    def comments(self, request, pk=None):
        try:
            post = CommunityPost.objects.get(pk=pk)
        except CommunityPost.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

# inventory/views.py (add these imports at the top if not already present)
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        # Create the user using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Generate a token for the new user
        token, created = Token.objects.get_or_create(user=user)
        data = serializer.data
        data["token"] = token.key
        return Response(data, status=status.HTTP_201_CREATED)

#logout function#

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Delete the user's token to invalidate it
        request.user.auth_token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
