from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    '''Модель тематических групп'''
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Уникальный адрес")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    '''Модель публикаций пользователей'''
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="post_author",
                               verbose_name="Автор")
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              blank=True, null=True,
                              verbose_name="Группа")
    image = models.ImageField(
        upload_to='posts/', blank=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.text


class Comment(models.Model):
    '''Модель комментариев к публикациям'''
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="commented_post",
                             verbose_name="Публикация")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comment_author",
                               verbose_name="Автор")
    text = models.TextField(verbose_name="Текст")
    created = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text


class Follow(models.Model):
    '''Модель подписки на публикации пользователя'''
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="follower",
                             verbose_name="Подписчик")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="following",
                               verbose_name="Избранный автор")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
