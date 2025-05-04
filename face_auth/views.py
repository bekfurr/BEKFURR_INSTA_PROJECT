import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
import json
import base64
from .models import FaceProfile, Post
from .face_utils import detect_face_from_image, verify_face

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    if request.user.is_authenticated and request.user.is_superuser:
        users = User.objects.all()
        return render(request, 'home.html', {'posts': posts, 'users': users})
    return render(request, 'home.html', {'posts': posts})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        face_image = request.POST.get('face_image')
        avatar = request.FILES.get('avatar')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username allaqachon mavjud')
            return render(request, 'register.html')
        
        if face_image:
            face_encoding = detect_face_from_image(face_image)
            if face_encoding is None:
                messages.error(request, 'Yuz tasvirida yuz aniqlanmadi')
                return render(request, 'register.html')
        else:
            messages.error(request, 'Yuz tasviri talab qilinadi')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, password=password)
        
        face_profile = FaceProfile(user=user)
        face_profile.set_encoding(face_encoding)
        if avatar:
            face_profile.avatar = avatar
        face_profile.save()
        
        messages.success(request, 'Ro‘yxatdan o‘tish muvaffaqiyatli! Endi tizimga kirishingiz mumkin.')
        return redirect('login')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_method = request.POST.get('login_method', 'password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Foydalanuvchi mavjud emas')
            return render(request, 'login.html')
        
        if login_method == 'password':
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Noto‘g‘ri ma’lumotlar')
        
        elif login_method == 'face':
            face_image = request.POST.get('face_image')
            if not face_image:
                messages.error(request, 'Yuz tasviri talab qilinadi')
                return render(request, 'login.html')
            
            try:
                face_profile = FaceProfile.objects.get(user=user)
                known_encoding = face_profile.get_encoding()
                if verify_face(known_encoding, face_image):
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Yuz tasdiqlanmadi')
            except FaceProfile.DoesNotExist:
                messages.error(request, 'Yuz profili topilmadi')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'user': request.user, 'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if not content:
            messages.error(request, 'Post mazmuni talab qilinadi')
            return redirect('dashboard')
        
        Post.objects.create(user=request.user, content=content, image=image)
        messages.success(request, 'Post muvaffaqiyatli yaratildi!')
        return redirect('dashboard')
    
    return render(request, 'create_post.html')

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        
        if not content:
            messages.error(request, 'Post mazmuni talab qilinadi')
            return render(request, 'edit_post.html', {'post': post})
        
        post.content = content
        if image:
            post.image = image
        post.save()
        messages.success(request, 'Post muvaffaqiyatli yangilandi!')
        return redirect('dashboard')
    
    return render(request, 'edit_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    messages.success(request, 'Post o‘chirildi!')
    return redirect('dashboard')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        avatar = request.FILES.get('avatar')
        
        if username and username != request.user.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username allaqachon mavjud')
                return render(request, 'edit_profile.html')
            request.user.username = username
            request.user.save()
        
        if avatar:
            face_profile, created = FaceProfile.objects.get_or_create(user=request.user)
            face_profile.avatar = avatar
            face_profile.save()
        
        messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
        return redirect('dashboard')
    
    return render(request, 'edit_profile.html')

@login_required
def manage_users(request):
    if not request.user.is_superuser:
        messages.error(request, 'Sizda foydalanuvchilarni boshqarish huquqi yo‘q')
        return redirect('dashboard')
    
    users = User.objects.all()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        try:
            target_user = User.objects.get(id=user_id)
            if action == 'delete':
                if target_user != request.user:  # Admin o‘zini o‘chira olmaydi
                    target_user.delete()
                    messages.success(request, 'Foydalanuvchi o‘chirildi')
                else:
                    messages.error(request, 'O‘zingizni o‘chira olmaysiz')
            
            elif action == 'edit':
                new_username = request.POST.get('new_username')
                if new_username and new_username != target_user.username:
                    if User.objects.filter(username=new_username).exists():
                        messages.error(request, 'Yangi username allaqachon mavjud')
                    else:
                        target_user.username = new_username
                        target_user.save()
                        messages.success(request, 'Foydalanuvchi ma’lumotlari yangilandi')
                else:
                    messages.error(request, 'Yangi username kiritilishi kerak')
            elif action == 'toggle_superuser':
                target_user.is_superuser = not target_user.is_superuser
                target_user.save()
                if target_user.is_superuser:
                    messages.success(request, 'Foydalanuvchi admin qilingan')
                else:
                    messages.success(request, 'Foydalanuvchi admin huquqi o‘chirildi')
            elif action == 'reset_password':
                new_password = uuid.uuid4().hex[:8] 
                target_user.set_password(new_password)
                target_user.save()
                messages.success(request, f'Foydalanuvchining paroli yangilandi: {new_password}')
            elif action == 'send_message':
                message = request.POST.get('message')
                if message:
                    # Bu yerda xabarni yuborish logikasini qo‘shing
                    messages.success(request, 'Xabar yuborildi')
                else:
                    messages.error(request, 'Xabar matni kiritilishi kerak')
        
        except User.DoesNotExist:
            messages.error(request, 'Foydalanuvchi topilmadi')
    
    return render(request, 'manage_users.html', {'users': users})

def capture_face_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image_data')
            if not image_data:
                return JsonResponse({'success': False, 'error': 'Tasvir ma’lumotlari yo‘q'})
            
            face_encoding = detect_face_from_image(image_data)
            if face_encoding is None:
                return JsonResponse({'success': False, 'error': 'Yuz aniqlanmadi'})
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Noto‘g‘ri so‘rov turi'})
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    for post in posts:
        post.views += 1  # Har ko‘rishda sonni oshirish
        post.save()
    if request.user.is_authenticated and request.user.is_superuser:
        users = User.objects.all()
        return render(request, 'home.html', {'posts': posts, 'users': users})
    return render(request, 'home.html', {'posts': posts})
@login_required
def dashboard(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    for post in posts:
        post.views += 1  # Har ko‘rishda sonni oshirish
        post.save()
    return render(request, 'dashboard.html', {'user': request.user, 'posts': posts})
