from django.db import models

class Player(models.Model):
    username = models.CharField(max_length=100)
    level = models.IntegerField(default=1)

    def __str__(self):
        return self.username
    
