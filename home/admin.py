from django.contrib import admin
from products.admin import super_admin_site
from . models import SliderArea, DisplayHotProductInCategories, PopularCategories, ContactMessage
from products.models import HelpVideo



super_admin_site.register(SliderArea)
super_admin_site.register(DisplayHotProductInCategories)
super_admin_site.register(PopularCategories)
super_admin_site.register(ContactMessage)