from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag

class PostList(ListView):
    model = Post
    ordering = '-pk'    # 최신순 정렬

    def get_context_data(self, **kwargs):   # ListView에서 내장하고 있는 메서드 model = post 하면 post_list = Post.objects.all()을 자동으로 명령 하는 등의 기능을 함, 오버라이딩 해서 가져오는 정보 추가
        context = super(PostList, self).get_context_data()     # 기존 get_context_data가 제공하던 기능 저장
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()      # 카테고리가 지정되지 않은 포스트 개수를 세서 쿼리셋으로 만들어 저장

        return context

# 설정 안하면 자동으로 post_list.html 을 인식
# template_name = 'blog/post_list.html'

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):   # 오버라이딩 해서 가져오는 정보 추가
        context = super(PostDetail, self).get_context_data()     # 기존 get_context_data가 제공하던 기능 저장
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()      # 카테고리가 지정되지 않은 포스트 개수를 세서 쿼리셋으로 만들어 저장

        return context

def category_page(request, slug):   # FBV방식으로 함수생성
    if slug == 'no_category':   # 미분류 목록을 클릭한 경우
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)  # URL에서 추출한 slug와 같은 slug를 갖는 카테고리를 불러오는 쿼리셋
        post_list = Post.objects.filter(category=category)   # 포스트 중에서 Category.objects.get(slug=slug)로 필터링한 카테고리만 가져옴을 의미

    return render(
        request,
        'blog/post_list.html',  # post_list.html을 사용하기 때문에 PostList 클래스에서 context로 정의 했던 부분을 딕셔너리 형태로 직접 정의해야한다.
        {
            'post_list': post_list,     # 앞에서 상황에 따라 저장되는 post_list
            'categories': Category.objects.all(),   # 카테고리 목록
            'no_category_post_count': Post.objects.filter(category=None).count(),   # 미분류 포스트 개수
            'category': category,   # 페이지 타이틀 옆에 카테고리 이름
        }
    )

def tag_page(request, slug):   # FBV방식으로 함수생성
    tag = Tag.objects.get(slug=slug)    # slug가 같은 태그를 불러오는 쿼리셋
    post_list = tag.post_set.all()  # 같은 태그를 가진 post를 모두 불러오기, 왜 카테고리랑 다르지?

    return render(
        request,
        'blog/post_list.html',  # post_list.html을 사용하기 때문에 PostList 클래스에서 context로 정의 했던 부분을 딕셔너리 형태로 직접 정의해야한다.
        {
            'post_list': post_list,     # 앞에서 상황에 따라 저장되는 post_list
            'tag' : tag,
            'categories': Category.objects.all(),   # 카테고리 목록
            'no_category_post_count': Post.objects.filter(category=None).count(),   # 미분류 포스트 개수
        }
    )


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