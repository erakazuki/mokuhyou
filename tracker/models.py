import secrets

from django.conf import settings
from django.db import models


def generate_slug():
    return secrets.token_urlsafe(12)


class CalendarRoom(models.Model):
    name = models.CharField('名前', max_length=100, default='筋トレカレンダー')
    slug = models.SlugField('共有URL', unique=True, default=generate_slug)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '共有カレンダー'
        verbose_name_plural = '共有カレンダー'

    def __str__(self):
        return self.name


class WorkoutEntry(models.Model):
    room = models.ForeignKey(
        CalendarRoom, on_delete=models.CASCADE, related_name='workouts'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workouts'
    )
    date = models.DateField('日付')

    class Meta:
        verbose_name = '筋トレ記録'
        verbose_name_plural = '筋トレ記録'
        unique_together = ['room', 'user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} - {self.date}'


class Goal(models.Model):
    room = models.ForeignKey(
        CalendarRoom, on_delete=models.CASCADE, related_name='goals'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals'
    )
    weekly_target = models.PositiveIntegerField(
        '週の目標回数', default=3, help_text='1週間に何回筋トレするか'
    )

    class Meta:
        verbose_name = '目標'
        verbose_name_plural = '目標'
        unique_together = ['room', 'user']

    def __str__(self):
        return f'{self.user.username}: 週{self.weekly_target}回'
