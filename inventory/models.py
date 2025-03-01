# inventory/models.py
from django.db import models
from django.contrib.auth.models import User

class PantryItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    expiration_date = models.DateField(null=True, blank=True)
    threshold = models.IntegerField(default=1)  # Defines low-stock level

    def __str__(self):
        return self.name

class Recipe(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.TextField(help_text="List ingredients (could be JSON or comma-separated)")
    instructions = models.TextField()
    popularity = models.IntegerField(default=0)  # Used for trending/popular recipes

    def __str__(self):
        return self.name

class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans")
    plan_name = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.plan_name

class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preference")
    dietary_restrictions = models.CharField(max_length=255, blank=True)
    favorite_cuisines = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences"

class InventoryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory_history")
    item = models.ForeignKey(PantryItem, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # e.g., "added", "removed", "used"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.action} at {self.timestamp}"

class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    trending_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Post {self.id} by {self.user.username}"

class Comment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
