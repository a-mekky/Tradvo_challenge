from django.contrib import admin

from apps.models import App


# Register your models here.

@admin.register(App)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'uploaded_by', 'apk_file_path', 'first_screen_screenshot_path', 'second_screen_screenshot_path', 'video_recording_path', 'ui_hierarchy', 'screen_changed', 'created_at', 'updated_at')
    search_fields = ('name', 'uploaded_by', 'id')
