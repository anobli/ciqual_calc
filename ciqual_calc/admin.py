from django.contrib import admin
from .models import Food

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = ('name', 'kcal_100g', 'protein_100g', 'carbs_100g', 'fat_100g')
    # Add a search bar in the admin to test queries
    search_fields = ('name',)
    # Add filters for quick sorting
    list_filter = ('kcal_100g',)
