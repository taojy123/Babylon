from django.contrib import admin

from app.models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'hidden', 'brick_tag', 'created_at']
    # list_filter = ['created_at']
    list_editable = ['hidden']
    list_max_show_all = 10000
    actions = ['save_pic']

    def save_pic(self, request, queryset):
        for r in queryset:
            r.save_pic()
