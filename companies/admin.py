from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name','industry','location','website')
    search_fields = ('name','industry','location')
    prepopulated_fields = {'slug': ('name',)}
