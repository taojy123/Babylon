from django.contrib import admin

from app.models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'key', 'created_at']
    list_filter = ['created_at']
    list_max_show_all = 10000
