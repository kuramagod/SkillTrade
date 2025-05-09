from django.contrib import admin

from .models import PostModel, ExChangeRequestModel, SkillsModel, UserSkills, ReviewModel

admin.site.register(PostModel)
admin.site.register(UserSkills)
admin.site.register(ReviewModel)

@admin.register(SkillsModel)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    prepopulated_fields = {"slug": ('name', )}
    list_display_links = ('id', 'name')
    ordering = ['id']

@admin.register(ExChangeRequestModel)
class ExChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'str_repr', 'status')
    list_display_links = ('id', 'str_repr', 'status')
    ordering = ['created_at']

    def str_repr(self, obj):
        return str(obj)

    str_repr.short_description = 'name'