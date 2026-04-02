from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from anime import views as anime_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', anime_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='anime/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('anime.urls')), 
]
