from django.contrib.auth import get_user_model
from django.db import models

from blogicum.constants import const

User = get_user_model()


class CreatedAtIsPublished(models.Model):
    """
    Абстрактный класс для двух полей:
    created_at - Добавлено;
    is_published - Опубликовано.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Title(models.Model):
    """
    Абстрактный класс для одного поля:
    title - Заголовок.
    """
    title = models.CharField(
        max_length=const.TITLE_LEN,
        verbose_name='Заголовок')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Location(CreatedAtIsPublished):
    """"
    Модель Локации с полями:
    created_at - Добавлено;
    is_published - Опубликовано;
    name - Название места.
    """
    name = models.CharField(
        max_length=const.TITLE_LEN,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(CreatedAtIsPublished, Title):
    """
    Модель Категории с полями:
    created_at - Добавлено;
    is_published - Опубликовано;
    title - Заголовок;
    description - Описание;
    slug - Идентификатор.
    """
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Post(CreatedAtIsPublished, Title):
    """
    Модель Посты с полями:
    created_at - Добавлено;
    is_published - Опубликовано;
    title - Заголовок;
    text - Текст;
    pub_date - Дата и время публикации;
    author - Автор публикации;
    image - Обложка поста;
    Связь с моделями: Локации, Категории, Комментарии.
    """
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно делать '
                  'отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='author_post'
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
        related_name='location_post'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='category_post'
    )
    image = models.ImageField('Фото', blank=True, upload_to='posts_images')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']


class Comment(models.Model):
    """
    Модель Комментариев к постам с полями:
    text - Текст комментария;
    post - Комментируемый пост;
    created_at - Дата создания;
    author - Автор комментария;
    Связь с моделями: Локации, Категории, Посты.
    """
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария')

    class Meta:
        ordering = ('created_at',)
