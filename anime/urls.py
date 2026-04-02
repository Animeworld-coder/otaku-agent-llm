from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # --- Main App Interface ---
    path('', views.character_search, name='character_search'),
    path('summon/<str:char_name>/', views.summon_character, name='summon_character'),
    path('chat/<int:char_id>/', views.chat_with_character, name='chat_character'),

    # --- Collection & Favorites ---
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('toggle-favorite/<int:char_id>/', views.toggle_favorite, name='toggle_favorite'),

    # --- Authentication (Neural Link Security) ---
    path('register/', views.register, name='register'),

    # Standard Login
    path('login/', auth_views.LoginView.as_view(template_name='anime/login.html'), name='login'),

    # Standard Logout (Redirects back to search after disconnecting)
    path('logout/', auth_views.LogoutView.as_view(next_page='character_search'), name='logout'),
]
