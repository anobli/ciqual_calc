from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=500)
    kcal_100g = models.FloatField(default=0)
    protein_100g = models.FloatField(default=0)
    carbs_100g = models.FloatField(default=0)
    fat_100g = models.FloatField(default=0)

    def __str__(self):
        return self.name
