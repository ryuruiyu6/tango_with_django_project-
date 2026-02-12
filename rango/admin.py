from django.contrib import admin

# Register your models here.
from django.contrib import admin
from rango.models import Category, Page, UserProfile

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'views', 'likes', 'slug')

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')
    list_filter = ('category',)
    search_fields = ('title',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)