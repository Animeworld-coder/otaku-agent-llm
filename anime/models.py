from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# 1. THE CHARACTER MODEL (Core AI Asset)
class Character(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    power_tier = models.CharField(max_length=100, default="Unknown")

    # FIXED: Changed URLField to TextField.
    # AI generated URLs can be massive; TextField prevents "Data too long" crashes.
    image_url = models.TextField(null=True, blank=True)
    wallpaper_url = models.TextField(null=True, blank=True)

    # Popularity & Engagement
    summon_count = models.PositiveIntegerField(default=1)
    # related_name='favorite_characters' makes the sidebar loop work perfectly
    favorites = models.ManyToManyField(User, related_name='favorite_characters', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. MEDIA GALLERIES
class CharacterImage(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='images')
    image_url = models.TextField() # Fixed to TextField

class CharacterVideo(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='videos')
    video_url = models.TextField() # Fixed to TextField

# 3. DYNAMIC CHAT SYSTEM
class ChatThread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    current_mood = models.CharField(max_length=50, default="Neutral")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} x {self.character.name} ({self.current_mood})"

class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=20) # 'user' or 'assistant'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# 4. USER PROFILE & ECONOMY
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_vip = models.BooleanField(default=False)

    # BigIntegerField supports your 1 Trillion Dev Scrolls without crashing the DB
    scrolls = models.BigIntegerField(default=100)

    # DateField ensures the "Daily Bonus" logic in views.py works correctly
    last_bonus_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} | Scrolls: {self.scrolls}"

# 5. TRANSACTION LOGS (Ready for Payment Integration)
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    verified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.reference} - {self.user.username}"

# --- CRITICAL: FIXED AUTOMATION SIGNALS ---
# This ensures every new user gets a Profile automatically without crashing.
@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # The 'hasattr' check prevents errors if a user is saved but has no profile
        if hasattr(instance, 'profile'):
            instance.profile.save()
