from django.db import models

# Create your models here.


class TestModel(models.Model):
    name = models.CharField(max_length=20)
    code = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.name)
