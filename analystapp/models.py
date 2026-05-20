from django.db import models

class LoginData(models.Model):

    username = models.CharField(max_length=100)
    email = models.EmailField(
    unique=True,
    null=True,
    blank=True
)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username