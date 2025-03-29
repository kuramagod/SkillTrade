from django.contrib import admin

from .models import PostModel, ExChangeRequestModel, SkillsModel, UserSkills, ReviewModel

admin.site.register(PostModel)
admin.site.register(ExChangeRequestModel)
admin.site.register(UserSkills)
admin.site.register(ReviewModel)

@admin.register(SkillsModel)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    prepopulated_fields = {"slug": ('name', )}
    list_display_links = ('id', 'name')
    ordering = ['id']
