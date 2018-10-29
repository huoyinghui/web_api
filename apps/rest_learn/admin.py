from django.contrib import admin

# Register your models here.
from .models import TestModel


@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    pass
