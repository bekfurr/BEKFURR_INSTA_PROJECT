from django.db import models
from django.contrib.auth.models import User
import numpy as np
import pickle
import base64

class FaceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_encoding = models.BinaryField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_encoding(self, encoding):
        if encoding is not None:
            self.face_encoding = pickle.dumps(encoding)
    
    def get_encoding(self):
        if self.face_encoding:
            return pickle.loads(self.face_encoding)
        return None
    
    def __str__(self):
        return f"Face profile for {self.user.username}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)  # Ko‘rishlar soni
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"