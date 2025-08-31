from products.models import Industry

def industry_categories(request):
    industries = Industry.objects.all()
    return {
        'industry': industries
    }