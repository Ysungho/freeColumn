from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post
from django.contrib.auth.models import User

class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

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
        # 1. 포스트 목록을 가지고 온다.
        response = self.client.get('/blog/')

        # 2. 정상적으로 페이지가 로드 된다.
        self.assertEqual(response.status_code, 200)

        # 3. 페이지의 타이틀은 'Blog'이다
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')

        # 4. 네이게이션 바의 존재 확인
        #navbar = soup.nav

        # 5. Blog, About Me 라는 문구 존재 확인
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('About Me', navbar.text)

        self.navbar_test(soup)

        # 6. 포스트가 한개도 없다면
        self.assertEqual(Post.objects.count(), 0)

        # 7. main area에 '아직 게시물이 없습니다' 문구가 나타난다.
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        # 8. 만약 포스트가 2개 있다면
        post_001 = Post.objects.create(
            title='첫번째 포스트입니다.',
            content='Hello World. We are the world.',
            author=self.user_trump
        )

        post_002 = Post.objects.create(
            title='두번째 포스트입니다.',
            content='1등이 전부는 아니잖아요?',
            author=self.user_obama
        )

        self.assertEqual(Post.objects.count(), 2)

        # 9. 포스트 목록 페이지를 새로고침 했을 때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)

        # 10. main area에 2개의 제목이 존재한다.
        main_area = soup.find('div', id='main-area')

        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)

        # 11. '아직 게시물이 없습니다.' 문구가 더 이상 나타나지 않는다.
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

    def test_post_detail(self):
        # 1.   Post가 하나 있다.
        post_001 = Post.objects.create(
            title='첫번째 포스트입니다.',
            content='Hello World. We are the world.',
            author=self.user_trump
        )
        # 2.  그 포스트의 url은 'blog/1/' 이다.
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        # 3.  첫 번째 post의 detail 페이지 테스트
        # 3.1  첫 번째 post url로 접근하면 정상적으로 작동한다. (status code: 200)
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 4.  post_list 페이지와 똑같은 네비게이션 바가 있다.
        #navbar = soup.nav  # beautifulsoup를 이용하면 간단히 페이지의 태그 요소에 접근이 가능합니다.
        #self.assertIn('Blog', navbar.text)
        #self.assertIn('About Me', navbar.text)
        self.navbar_test(soup)


        # 5.  첫 번째 post의 title이 브라우저 탭에 표기되는 페이지 title에 있다.
        self.assertIn(post_001.title, soup.title.text)

        # 6.  첫 번째 post의 title이 post-area에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)

        # 7.  첫 번째 post의 작성자(author)가 post-area에 있다.
        self.assertIn(self.user_trump.username.upper(), post_area.text)

        # 8.  첫 번째 post의 content가 post-area에 있다.
        self.assertIn(post_001.content, post_area.text)
