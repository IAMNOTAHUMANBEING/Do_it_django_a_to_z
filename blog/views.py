from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category

class PostList(ListView):
    model = Post
    ordering = '-pk'    # 최신순 정렬

    def get_context_data(self, **kwargs):   # ListView에서 내장하고 있는 메서드 model = post 하면 post_list = Post.objects.all()을 자동으로 명령 하는 등의 기능을 함, 오버라이딩 해서 가져오는 정보 추가
        context = super(PostList, self).get_context_data()     # 기존 get_context_data가 제공하던 기능 저장
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()      # 카테고리가 지정되지 않은 포스트 개수를 세서 쿼리셋으로 만들어 저장

        return context

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):   # 오버라이딩 해서 가져오는 정보 추가
        context = super(PostDetail, self).get_context_data()     # 기존 get_context_data가 제공하던 기능 저장
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()      # 카테고리가 지정되지 않은 포스트 개수를 세서 쿼리셋으로 만들어 저장

        return context



    # 설정 안하면 자동으로 post_list.html 을 인식
    # template_name = 'blog/post_list.html'
# FBV 방식
# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#
#     return render(
#         request,
#         'blog/post_list.html',
#         {
#             'posts': posts,
#         }
#     )
#
# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post':post,
#         }
#     )