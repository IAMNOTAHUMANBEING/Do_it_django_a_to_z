from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag, Comment
from django.contrib.auth.models import User


class TestView(TestCase):
    def setUp(self):
        self.client = Client()  # Client: 테스트를 위한 가상의 사용자
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.user_obama.is_staff = True  # 스태프 권한 부여
        self.user_obama.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title='첫번째 포스트입니다',
            content='Hello World. We are the world',
            category=self.category_programming,
            author=self.user_trump,
        )
        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두번째 포스트입니다',
            content='1등이 전부는 아니잖아요?',
            category=self.category_music,
            author=self.user_obama,
        )
        self.post_003 = Post.objects.create(
            title='세번째 포스트입니다',
            content='category가 없을 수도 있죠',
            author=self.user_obama,
        )
        self.post_003.tags.add(self.tag_python)
        self.post_003.tags.add(self.tag_python_kor)

        self.comment_001 = Comment.objects.create(
            post=self.post_001,
            author=self.user_obama,
            content='첫 번째 댓글입니다. ',
        )

    def test_category_page(self):
        # 카테고리 페이지 읽어오기
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 페이지 상단 카테고리 뱃지 존재
        self.assertIn(self.category_programming.name, soup.h1.text)

        # 메인영역에 카테고리 이름 있는지 확인, 이 카테고리에 해당하는 포스트만 노출 되는지 확인
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_music.name}({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)

        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

    def test_post_detail(self):
        # 1. 포스트의 url은 'blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 2. 첫번째 포스트의 상세 페이지 테스트
        # 2.1 첫번째 post url로 접근하면 정상적으로 작동한다
        response = self.client.get(self.post_001.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2.2 네비게이션 바와 카테고리 목록이 존재한다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 2.3 첫번째 포스트의 제목(title)이 웹 브라우저 탭 타이틀에 들어있다.
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4 첫번째 포스트의 제목과 카테고리가 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        # 2.5 첫번째 포스트의 작성자(author)가 포스트 영역에 있다.
        self.assertIn(self.user_trump.username.upper(), post_area.text)

        # 2.6 첫번째 포스트의 내용(content)이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        # 2.7 첫번째 포스트의 태그가 포스트 영역에 있다.
        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)

        # comment area
        comments_area = soup.find('div', id='comment-area')
        comment_001_area = comments_area.find('div', id='comment-1')
        self.assertIn(self.comment_001.author.username, comment_001_area.text)
        self.assertIn(self.comment_001.content, comment_001_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)

        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 로그인하지 않으면 status code가 200이면 안 된다
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 trump가 로그인 한다
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 obama로 로그인 한다
        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')  # tag input이 존재하는지 확인
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',  # 해당 경로로
            {
                'title': 'Post Form 만들기',
                'content': 'Post Form 페이지를 만듭시다.',  # 딕셔너리 정보를 Post 방식으로 전송
                'tags_str': 'new tag; 한글태그, python',
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")  # 마지막 게시물 즉, 전송한 게시물 정보가 잘 저장됐는지 확인
        self.assertEqual(last_post.author.username, 'obama')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글태그'))
        self.assertTrue(Tag.objects.count(), 5)

    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(username=self.user_trump.username, password='somepassword')
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자(obama)가 접근하는 경우
        self.client.login(
            username=self.post_003.author.username,
            password='somepassword',
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('파이썬 공부;python', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세번째 포스트를 수정했습니다.',
                'content': '안녕 세계? 우리는 하나!',
                'category': self.category_music.pk,  # pk 값을 명시해야함
                'tags_str': '파이썬 공부;한글태그, some tag'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('안녕 세계? 우리는 하나!', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)
        self.assertIn('한글태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertNotIn('python', main_area.text)

    def test_comment_form(self):
        self.assertEqual(Comment.objects.count(), 1)  # setUp() 함수에 이미 댓글이 하나 있는 상태에서 시작합니다
        self.assertEqual(self.post_001.comment_set.count(), 1)  # 위 댓글은 post_001에 달려있는지 확인

        # 로그인 하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertIn('Log in and leave a comment', comment_area.text)  # 로그인 하라는 메세지 출력
        self.assertFalse(comment_area.find('form', id='comment-form'))  # form이 안보여야함

        # 로그인 한 상태
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('Log in and leave a comment', comment_area.text)

        comment_form = comment_area.find('form', id='comment-form')
        self.assertTrue(comment_form.find('textarea', id='id_content'))
        response = self.client.post(  # POST방식으로 댓글 내용을 서버로 전달, 요청결과를 response에 저장
            self.post_001.get_absolute_url() + 'new_comment/',
            {
                'content': "오바마의 댓글입니다.",
            },
            follow=True  # POST로 보내는 경우 서버에서 처리한 후 리다이렉트 되는데 이때 따라가도록 설정하는 역할
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 2)  # 댓글이 추가 됐으므로 2개
        self.assertEqual(self.post_001.comment_set.count(), 2)

        new_comment = Comment.objects.last()  # 마지막으로 생성된 comment 가져오기

        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(new_comment.post.title,
                      soup.title.text)  # POST 방식으로 서버에 요청하면 comment가 달린 상세 페이지가 response에 리다이렉트 됨. 마지막 생성된 comment와 일치하는지 비교

        comment_area = soup.find('div', id='comment-area')
        new_comment_div = comment_area.find('div', id=f'comment-{new_comment.pk}')
        self.assertIn('obama', new_comment_div.text)
        self.assertIn("오바마의 댓글입니다.", new_comment_div.text)

    def test_comment_update(self):
        comment_by_trump = Comment.objects.create(
            post=self.post_001,
            author=self.user_trump,
            content='트럼프의 댓글입니다.'
        )

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))
        self.assertFalse(comment_area.find('a', id='comment-1-update-btn'))

        # 로그인 한 상태
        self.client.login(username='obama', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-2-update-btn'))     # obama로 로그인 했으므로 trump가 작성한 댓글에 수정버튼 안보여야함
        comment_001_update_btn = comment_area.find('a', id='comment-1-update-btn')
        self.assertIn('edit', comment_001_update_btn.text)  # obama가 작성한 comment_001에 대한 edit 수정버튼이 나타나야함
        self.assertEqual(comment_001_update_btn.attrs['href'], '/blog/update_comment/1/')   # 버튼에는 링크 경로를 담은 href 속성이 있어야함

        response = self.client.get('/blog/update_comment/1/')   # edit 버튼을 누르면 댓글을 수정하는 폼이 있는 페이지로 넘어감
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Comment - Blog', soup.title.text)
        update_comment_form = soup.find('form', id='comment-form')
        content_textarea = update_comment_form.find('textarea', id='id_content')
        self.assertIn(self.comment_001.content, content_textarea.text)  # textarea 안에 수정하기 전 comment 내용이 담겨있다

        response = self.client.post(    # 폼의 content 내용을 수정하고 submit 버튼을 클릭하면 댓글이 수정된다
            f'/blog/update_comment/{self.comment_001.pk}/',
            {
                'content': "오바마의 댓글을 수정합니다.",
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_001_div = soup.find('div', id='comment-1')
        self.assertIn('오바마의 댓글을 수정합니다.', comment_001_div.text)
        self.assertIn('Updated: ', comment_001_div.text)    # 수정되었다는 표시가 존재

    def test_delete_comment(self):
        comment_by_trump = Comment.objects.create(  # trump 이름으로 댓글 작성
            post=self.post_001,
            author=self.user_trump,
            content='트럼프의 댓글입니다.',
        )

        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(self.post_001.comment_set.count(), 2)

        # 로그인하지 않은 상태
        response = self.client.get(self.post_001.get_absolute_url())    # 로그인 하지 않은 상태에서는 post_001의 페이지에 댓글 삭제가 보이면 안됨
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        self.assertFalse(comment_area.find('a', id='comment-2-delete-btn'))

        # trump로 로그인한 상태
        self.client.login(username='trump', password='somepassword')
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        comment_area = soup.find('div', id='comment-area')      # trump로 로그인 했기 때문에 obama가 작성한 댓글에는 삭제버튼이 없고 pk=2인 댓글에만 있어야함
        self.assertFalse(comment_area.find('a', id='comment-1-delete-btn'))
        comment_002_delete_modal_btn = comment_area.find(
            'a', id='comment-2-delete-modal-btn'
        )
        self.assertIn('delete', comment_002_delete_modal_btn.text)  # 버튼을 누르면 곧바로 지우지 않고 한 번 더 묻는 modal 창을 띄움
        self.assertEqual(
            comment_002_delete_modal_btn.attrs['data-target'],
            '#deleteCommentModal-2'
        )

        delete_comment_modal_002 = soup.find('div', id='deleteCommentModal-2')  # 삭제할지 묻는 질문과 링크를 담은 버튼 존재
        self.assertIn('Are You Sure?', delete_comment_modal_002.text)
        really_delete_btn_002 = delete_comment_modal_002.find('a')
        self.assertIn("Delete", really_delete_btn_002.text)
        self.assertEqual(
            really_delete_btn_002.attrs['href'],
            '/blog/delete_comment/2/'
        )

        response = self.client.get('/blog/delete_comment/2/', follow=True)  # 실제로 delete를 누르면 댓글이 삭제되고 post_001로 리다이렉트
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertIn(self.post_001.title, soup.title.text)
        comment_area = soup.find('div', id='comment-area')
        self.assertNotIn('트럼프의 댓글입니다.', comment_area.text)

    def test_search(self):
        post_about_python = Post.objects.create(
            title='파이썬에 대한 포스트입니다.',
            content='Hello World. We are the world.',
            author=self.user_trump,
        )

        response = self.client.get('/blog/search/파이썬/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        main_area = soup.find('div', id='main-area')

        self.assertIn('Search: 파이썬 (2)', main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertIn(self.post_003.title, main_area.text)
        self.assertIn(post_about_python.title, main_area.text)






