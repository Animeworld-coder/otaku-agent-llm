import os
import json
import random
import time
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from groq import Groq
from duckduckgo_search import DDGS
from .models import Character, ChatThread, ChatMessage, Profile

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 1. FIXED SEARCH HELPER (Updated for latest DDGS API)
def get_character_facts(name):
    try:
        with DDGS() as ddgs:
            search_query = f"{name} anime character personality wiki"
            # Using list comprehension to safely get the body text
            results = [r['body'] for r in ddgs.text(search_query, max_results=3)]
            if results:
                return "\n".join(results)
    except Exception as e:
        print(f"Fact Search Error: {e}")
    return "No specific web data found."

# 2. FIXED IMAGE HELPER (Corrected list indexing)
def get_real_character_art(name):
    try:
        with DDGS() as ddgs:
            search_query = f"{name} anime official character art high res"
            # size='Large' helps get high-quality images
            results = list(ddgs.images(search_query, region="wt-wt", safesearch="off", size="Large", max_results=5))

            if results:
                # Safely get the image URL from the dictionary
                profile_url = results[0].get('image')
                # Try to get a different second image for wallpaper
                wallpaper_url = results[1].get('image') if len(results) > 1 else profile_url
                return profile_url, wallpaper_url
    except Exception as e:
        print(f"Image Search Error: {e}")

    # Standard high-quality fallback placeholders
    return "https://alphacoders.com", "https://alphacoders.com"

# 3. SEARCH VIEW
def character_search(request):
    query = request.GET.get('q', '').strip()
    result = Character.objects.filter(name__icontains=query).first() if query else None

    if query and not result:
        return redirect('summon_character', char_name=query)

    leaderboard = Character.objects.order_by('-summon_count')[:10]
    scrolls = 0
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        # Admin / Superuser bonus
        if request.user.username == 'emptybrain' or request.user.is_superuser:
            profile.scrolls = 1000000
            profile.save()

        # Daily login bonus
        today = timezone.now().date()
        if profile.last_bonus_date < today:
            profile.scrolls += 100
            profile.last_bonus_date = today
            profile.save()
        scrolls = profile.scrolls

    return render(request, 'anime/index.html', {
        'character': result,
        'query': query,
        'scrolls': scrolls,
        'leaderboard': leaderboard
    })

# 4. CHAT LOGIC
@login_required
def chat_with_character(request, char_id):
    character = get_object_or_404(Character, id=char_id)
    thread, _ = ChatThread.objects.get_or_create(user=request.user, character=character)
    client = Groq(api_key=GROQ_API_KEY)

    if request.method == "POST":
        user_message = request.POST.get("message")
        if user_message:
            ChatMessage.objects.create(thread=thread, role='user', content=user_message)
            try:
                history_objs = thread.messages.all().order_by('-timestamp')[:10]
                history_objs = reversed(list(history_objs))

                groq_messages = [
                    {"role": "system", "content": f"You are {character.name}. Bio: {character.description}. Be dynamic. If insulted, get ANGRY. Start every reply with a mood tag: [MOOD: Value]."}
                ]
                for msg in history_objs:
                    groq_messages.append({"role": msg.role, "content": msg.content})

                chat_res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    messages=groq_messages
                )
                raw_text = chat_res.choices[0].message.content

                # Parse Mood
                if "[MOOD:" in raw_text:
                    try:
                        parts = raw_text.split("]", 1)
                        thread.current_mood = parts[0].replace("[MOOD:", "").strip()
                        ai_text = parts[1].strip() if len(parts) > 1 else raw_text
                    except:
                        ai_text = raw_text
                else:
                    ai_text = raw_text

                thread.save()
                ChatMessage.objects.create(thread=thread, role='assistant', content=ai_text)
            except Exception as e:
                messages.error(request, f"Neural link failed: {str(e)}")
        return redirect('chat_character', char_id=char_id)

    chat_history = thread.messages.all().order_by('timestamp')
    return render(request, 'anime/chat.html', {
        'character': character,
        'chat_history': chat_history,
        'mood': thread.current_mood
    })

# 5. FIXED SUMMON LOGIC
@login_required
def summon_character(request, char_name):
    profile = request.user.profile
    if profile.scrolls < 1:
        messages.error(request, "Insufficient Scrolls.")
        return redirect('character_search')

    clean_name = char_name.strip().title()
    char = Character.objects.filter(name__iexact=clean_name).first()

    if not char:
        try:
            # Step 1: Get Facts
            web_facts = get_character_facts(clean_name)

            # Step 2: Get Images
            profile_url, wallpaper_url = get_real_character_art(clean_name)

            # Step 3: Llama Bio Generation
            client = Groq(api_key=GROQ_API_KEY)
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a factual anime historian. Use provided web data to create a concise, cool bio."},
                    {"role": "user", "content": f"CHARACTER: {clean_name}\nDATA: {web_facts}"}
                ]
            )

            char = Character.objects.create(
                name=clean_name,
                description=comp.choices[0].message.content,
                image_url=profile_url,
                wallpaper_url=wallpaper_url
            )
            profile.scrolls -= 1
            profile.save()
            messages.success(request, f"{clean_name} Neural Sequence Saved!")
        except Exception as e:
            messages.error(request, f"Summoning failed: {str(e)}")
            return redirect('character_search')
    else:
        char.summon_count += 1
        char.save()

    return redirect(f"/?q={clean_name}")

@login_required
def favorites_list(request):
    return render(request, 'anime/favorites.html', {'favorites': request.user.favorite_characters.all()})

@login_required
def toggle_favorite(request, char_id):
    character = get_object_or_404(Character, id=char_id)
    if character.favorites.filter(id=request.user.id).exists():
        character.favorites.remove(request.user)
    else:
        character.favorites.add(request.user)
    return redirect(f"/?q={character.name}")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration Complete.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'anime/register.html', {'form': form})
