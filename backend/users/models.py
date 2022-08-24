from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=150, unique=True,
                              verbose_name='Email')
    username = models.CharField(blank=False, max_length=150, unique=True,
                                verbose_name='Username')
    first_name = models.CharField(blank=False, max_length=150,
                                  verbose_name='Name')
    last_name = models.CharField(blank=False, max_length=150,
                                 verbose_name='Surname')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='User-follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='following',
                                  verbose_name='User-following')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'following'],
                       name='unique_following')]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
