from django.contrib.auth.models import User
from face_auth.models import Post

def site_stats(request):
    return {
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
    }