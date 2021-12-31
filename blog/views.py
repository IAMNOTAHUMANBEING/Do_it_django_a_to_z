from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class PostList(ListView):
    model = Post
    ordering = '-pk'  # 최신순 정렬
    paginate_by = 5

    def get_context_data(self,
                         **kwargs):  # ListView에서 내장하고 있는 메서드 model = post 하면 post_list = Post.objects.all()을 자동으로 명령 하는 등의 기능을 함, 오버라이딩 해서 가져오는 정보 추가
        context = super(PostList, self).get_context_data()  # 기존 get_context_data가 제공하던 기능 저장
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(
            category=None).count()  # 카테고리가 지정되지 않은 포스트 개수를 세서 쿼리셋으로 만들어 저장

        return context


# 설정 안하면 자동으로 post_list.html 을 인식
# template_name = 'blog/post_list.html'

class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):  # 오버라이딩 해서 가져오는 정보 추가
        context = super(PostDetail, self).get_context_data()  # 기존 get_context_data가 제공하던 기능 저장
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(
            category=None).count()  # 카테고리가 지정되지 않은 포스트 개수를 세서 쿼리셋으로 만들어 저장
        context['comment_form'] = CommentForm
        return context


def category_page(request, slug):  # FBV방식으로 함수생성
    if slug == 'no_category':  # 미분류 목록을 클릭한 경우
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)  # URL에서 추출한 slug와 같은 slug를 갖는 카테고리를 불러오는 쿼리셋
        post_list = Post.objects.filter(
            category=category)  # 포스트 중에서 Category.objects.get(slug=slug)로 필터링한 카테고리의 포스트만 가져옴을 의미

    return render(
        request,
        'blog/post_list.html',  # post_list.html을 사용하기 때문에 PostList 클래스에서 context로 정의 했던 부분을 딕셔너리 형태로 직접 정의해야한다.
        {
            'post_list': post_list,  # 앞에서 상황에 따라 저장되는 post_list
            'categories': Category.objects.all(),  # 카테고리 목록
            'no_category_post_count': Post.objects.filter(category=None).count(),  # 미분류 포스트 개수
            'category': category,  # 페이지 타이틀 옆에 카테고리 이름
        }
    )


def tag_page(request, slug):  # FBV방식으로 함수생성
    tag = Tag.objects.get(slug=slug)  # slug가 같은 태그를 불러오는 쿼리셋
    post_list = tag.post_set.all()  # 같은 태그를 가진 post를 모두 불러오기, 왜 카테고리랑 다르지?

    return render(
        request,
        'blog/post_list.html',  # post_list.html을 사용하기 때문에 PostList 클래스에서 context로 정의 했던 부분을 딕셔너리 형태로 직접 정의해야한다.
        {
            'post_list': post_list,  # 앞에서 상황에 따라 저장되는 post_list
            'tag': tag,
            'categories': Category.objects.all(),  # 카테고리 목록
            'no_category_post_count': Post.objects.filter(category=None).count(),  # 미분류 포스트 개수
        }
    )


class PostCreate(UserPassesTestMixin, LoginRequiredMixin, CreateView):  # Mixin 클래스는 추가 상속이 가능
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', ]  # 사용자에게 입력 받을 요소

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff  # 접근가능한 사용자를 제한

    def form_valid(self, form):  # form 안에 들어온 값을 바탕으로 모델에 해당하는 인스턴스를 만들어 데이터베이스에 저장한 후 그 인스턴스의 경로로 리다이렉트 하는 역할
        current_user = self.request.user  # 웹사이트 방문자 의미
        if current_user.is_authenticated and (
                current_user.is_staff or current_user.is_suqeruser):  # 방문자가 로그인한 상태인지, 권한을 가지고 있는지 확인
            form.instance.author = current_user  # 방문한 상태면 form.instance(새로 생성한 포스트)의 author 필드에 current_user(현재 접속한 방문자)를 담는다.
            response = super(PostCreate, self).form_valid(form)  # 태그와 관련된 작업을 하기 전에 현재의 form을 인자로 보내 결과를 담아둠

            tags_str = self.request.POST.get('tags_str')  # Post 방식으로 전달된 정보 중 name='tags_str'인 input의 값을 가져오라는 의미
            if tags_str:
                tags_str = tags_str.strip()  # 문자열 공백 제거

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(
                        name=t)  # 같은 name을 갖는 tag가 있다면 가져오고 없으면 새로 만듬, Tag모델 인스턴스와 인스턴스가 새로생성되었는지 나타내는 bool을 리턴
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)  # 새로 생성하는 경우 slug도 만들어줘야함
                        tag.save()
                    self.object.tags.add(tag)  # 새로 만든 post의 tags 필드에 tag 추가

            return response  # 처리한 form을 기본 form_valid() 함수에 인자로 보내서 처리
        else:
            return redirect('/blog/')  # 로그인한 상태가 아니라면 이전 주소로 되돌려 보냄


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:  # 방문자(request.user)는 로그인한 상태이고 Post의 author와 동일해야함
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)  # 만족하면 기존 dispatch 기능 작동
        else:
            raise PermissionDenied  # 만족하지 않으면 403 오류 메시지 나타냄

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()  # 템플릿으로 추가인자 넘기는 기능
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = ';'.join(tags_str_list)  # ;으로 결합하여 return 하면 템플릿에서 해당 위치를 채움

        return context

    def form_valid(self, form):  # PostCreate에 사용한 것 재사용
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()  # 가져온 포스트의 태그를 모두 제거하고 수정된 내용으로 채우기

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',', ';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response

def new_comment(request, pk):
    if request.user.is_authenticated:  # 로그인 하지 않은 경우 댓글폼이 보이지 않게 했지만 비정상적 방법으로 접근하려는 시도가 있을 경우 대비
        post = get_object_or_404(Post, pk=pk)  # 댓글을 달 포스트를 쿼리를 날려서 가져오기 없으면 404 오류 발생시키기

        if request.method == 'POST':  # Submit를 클릭하면 POST방식으로 전달 됨. 직접 브라우저로 입력하여 접근하는 경우 GET방식으로 접근하게 되므로 해당 포스트 페이지로 리다이렉트 시킴
            comment_form = CommentForm(
                request.POST)  # 정상적으로 폼을 작성하고 POST 방식으로 서버에 요청이 들어왔다면 POST방식으로 들어온 정보를 comment form 형태로 가져옴
            if comment_form.is_valid():  # form이 유효하게 작성됐다면 해당 내용으로 새로운 레코드를 만들어 DB에 저장
                comment = comment_form.save(commit=False)  # 바로 저장하지 않고 연기
                comment.post = post
                comment.author = request.user
                comment.save()  # post, author field를 채움
                return redirect(comment.get_absolute_url())  # 해당 포스트의 상세페이지에서 댓글이 작성된 위치로 이동
            else:
                return redirect(post.get_absolute_url())

        else:
            raise PermissionDenied

class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):   
        if request.user.is_authenticated and request.user == self.get_object().author:  # 로그인이 되었고 작성자와 같은 사람인지 확인 후
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)     # Get 방식인지 Post 방식인지 판단하는 기본 기능 실행
        else:
            raise PermissionDenied

def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk) # 함수에서 인자로 받은 pk값과 같은 값을 가진 댓글을 쿼리셋으로 가져옴
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied



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
