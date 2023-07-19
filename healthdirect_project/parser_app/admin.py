from django.contrib import admin

from parser_app.models import Info


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ('practitioner_name', 'name', 'address', 'phone', 'email', 'website',
                    'practitioner_profession', 'practitioner_sex', 'practitioner_lang')
