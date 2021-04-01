from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.urls import reverse
import tempfile
from django.conf import settings
import shutil
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm
from django.core.cache import cache

User = get_user_model()


class PostCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.author = User.objects.create(username='user')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_desc'
        )

        cls.post = Post.objects.create(
            text='test_text',
            author=cls.author,
            group=cls.group
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = PostCreateTest.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_form_edit_post(self):
        """При редактировании поста через форму на странице
        /<username>/<post_id>/edit/
        изменяется соответствующая запись в базе данных."""
        form_data = {'group': self.group.id,
                     'text': 'modified-post',
                     }
        self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': self.user,
                'post_id': self.post.id
            }),
            data=form_data,
            follow=True
        )

        self.post.refresh_from_db()
        self.assertEqual(self.post.text, form_data['text'])

    def test_create_post_with_image(self):
        """Валидная форма создает запись в Post with image."""
        tasks_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {'group': PostCreateTest.group.id,
                     'text': 'test_text',
                     'image': uploaded,
                     }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(Post.objects.filter(
            group=PostCreateTest.group).exists())
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(Post.objects.first().image)
