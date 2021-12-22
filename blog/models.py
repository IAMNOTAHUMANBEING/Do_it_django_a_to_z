from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=30)     # 글씨 제한이 있는 문자 필드
    content = models.TextField()     # 길이제한이 없는 텍스트 필드 

    created_at = models.DateTimeField(auto_now_add=True)     # 월,일,시,분,초 까지 작성일 기록 필드
    updated_at = models.DateTimeField(auto_now=True)
    # author: 추후 작성 예정

    def __str__(self):
        return f'[{self.pk}]{self.title}'
