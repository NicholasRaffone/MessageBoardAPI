from django.db import models
class Post(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()
    is_admin = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    xpos = models.IntegerField()
    ypos = models.IntegerField()
    color = models.CharField(max_length=10)
    def __str__(self):
        return self.title
