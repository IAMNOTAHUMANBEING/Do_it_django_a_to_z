from django.contrib import admin
from .models import Post, Category

admin.site.register(Post)

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}  # category 모델의 name 필드에 값이 입력되면 자동으로 slug가 생성됨

admin.site.register(Category, CategoryAdmin)
