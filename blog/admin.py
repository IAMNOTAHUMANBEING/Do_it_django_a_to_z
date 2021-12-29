from django.contrib import admin
from .models import Post, Category, Tag, Comment

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}  # category 모델의 name 필드에 값이 입력되면 자동으로 slug가 생성됨

class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}

admin.site.register(Category, CategoryAdmin)    # admin페이지에서 사용할 수 있도록 등록
admin.site.register(Tag, TagAdmin)
admin.site.register(Post)
admin.site.register(Comment)

