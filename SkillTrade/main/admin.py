from django.contrib import admin

from .models import PostModel, CategoryModel, ExChangeRequestModel, SkillsModel, UserSkills, ReviewModel

admin.site.register(PostModel)
admin.site.register(ExChangeRequestModel)
admin.site.register(SkillsModel)
admin.site.register(UserSkills)
admin.site.register(ReviewModel)

@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    prepopulated_fields = {"slug": ('name', )}
    list_display_links = ('id', 'name')
    ordering = ['id']
