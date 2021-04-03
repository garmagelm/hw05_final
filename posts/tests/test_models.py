from django.test import TestCase
from posts.models import Post, User, Group


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название',
            slug='Ссылка',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=User.objects.create(username='user'),
        )

    def test_verbose_name(self):
        """Тестируем содержание verbose."""
        post = PostsModelTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """Тестируем содержание help_texts."""
        post = PostsModelTest.post
        field_help_texts = {
            'group': 'Выберите группу',
            'text': 'Напишите текст',
            'image': 'Загрузите изображение',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_object_name_is_text_field(self):
        """Проверка, что str сокращает текст поста до 15 символов."""
        post = PostsModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group_title(self):
        """Проверка, что str корректно выдает название группы."""
        group = PostsModelTest.group
        title = str(group)
        self.assertEqual(title, group.title)
