from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, Skill

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Profile', {'fields': ('headline','bio','profile_image','location',
                                'is_available_for_hire','available_from','availability_note',
                                'skills','is_company_admin')}),
    )
    list_display = ('username','email','first_name','last_name','is_company_admin','is_available_for_hire','is_staff','is_active')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ('name',)
