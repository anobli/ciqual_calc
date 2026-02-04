from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField
from .models import Food

# This is the function the error is complaining about!
def index(request):
    return render(request, 'ciqual_calc/index.html')

def food_search(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    # Search logic with priority for "starts with"
    results = Food.objects.filter(name__icontains=query).annotate(
        priority=Case(
            When(name__iexact=query, then=Value(1)),
            When(name__istartswith=f"{query},", then=Value(2)),
            When(name__istartswith=query, then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('priority', 'name')[:30]

    data = [{
        'id': f.id, 
        'text': f.name, 
        'kcal': f.kcal_100g,
        'protein': f.protein_100g,
        'carbs': f.carbs_100g,
        'fat': f.fat_100g
    } for f in results]

    return JsonResponse({'results': data})
