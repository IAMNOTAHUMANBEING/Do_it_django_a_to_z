from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
import os

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)    # 사람이 읽을 수 있는 텍스트로 고유 URL을 만듬

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'   # 마지막에 / 안넣어서 시간 날림

    class Meta:
        verbose_name_plural = 'Categories'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)    # 사람이 읽을 수 있는 텍스트로 고유 URL을 만듬

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'   # 마지막에 / 안넣어서 시간 날림

class Post(models.Model):
    title = models.CharField(max_length=30)  # 글씨 제한이 있는 문자 필드
    hook_text = models.CharField(max_length=100, blank=True)  # 미리보기 내용
    content = models.TextField()  # 길이제한이 없는 텍스트 필드
    # content = MarkdownxField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 월,일,시,분,초 까지 작성일 기록 필드
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # 사용자가 삭제되면 작성자 null로 변환
    # author = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자가 삭제되면 작성한 포스트도 삭제

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)    # black와 null

    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):  # 페이지의 주소를 가져오는 함수
        return f'/blog/{self.pk}/'

    def get_file_name(self):  # 업로드 파일 이름 가져오는 함수
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):  # 파일 이름에서 확장자만 리턴하는 함수
        return self.get_file_name().split('.')[-1]

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/505/cac0f057ee2aa45a/svg/{self.author.email}'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)    # 여러 댓글이 한 포스트의 댓글이 되므로 post필드에 ForeignKey 사용
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)    # 처음 생성될 때 시간 자동 저장
    modified_at = models.DateTimeField(auto_now=True)   # 저장될 때 시간 자동 저장

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'  # '#'은 HTML 요소의 id를 의미, 해당 포스트 페이지를 열고 comment-{self.pk}에 해당하는 위치로 이동함을 의미

    def get_avatar_url(self):
        if self.author.socialaccount_set.exists():
            return self.author.socialaccount_set.first().get_avatar_url()
        else:
            return f'https://doitdjango.com/avatar/id/505/cac0f057ee2aa45a/svg/{self.author.email}'
    
                             

