from django.db import models
from django.contrib.auth.models import User
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

class Post(models.Model):
    title = models.CharField(max_length=30)  # 글씨 제한이 있는 문자 필드
    hook_text = models.CharField(max_length=100, blank=True)  # 미리보기 내용
    content = models.TextField()  # 길이제한이 없는 텍스트 필드

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 월,일,시,분,초 까지 작성일 기록 필드
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)  # 사용자가 삭제되면 작성자 null로 변환
    # author = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자가 삭제되면 작성한 포스트도 삭제

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)    # black와 null 구분

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):  # 페이지의 주소를 가져오는 함수
        return f'/blog/{self.pk}/'

    def get_file_name(self):  # 업로드 파일 이름 가져오는 함수
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):  # 파일 이름에서 확장자만 리턴하는 함수
        return self.get_file_name().split('.')[-1]


