from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models import Count, Q
from django.views.decorators.http import require_POST, require_GET
from .models import Post, Reply, PostLike, ReplyLike, Follow, Notification, Hashtag
from .models import Job, Notification
from .models import Project
from .forms import PostForm, ReplyForm, ProfileForm
from .forms import ProjectForm
from .utils import handle_hashtags, handle_mentions_on_post, handle_mentions_on_reply, extract_youtube_id
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect
from .models import Company, Job, UserProfile, Skill
from .forms import UserProfileForm, CompanyForm, JobForm
from .models import Job, Skill
from django.http import JsonResponse
from django.template.loader import render_to_string
import base64
from django.core.files.base import ContentFile
from django.contrib import messages


@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.youtube_id = extract_youtube_id(post.content)
        post.save()

        # 🔊 Sprachnachricht verarbeiten
        if request.POST.get("audio_data"):
            audio_data = request.POST["audio_data"]
            format, audio_str = audio_data.split(";base64,")
            audio_file = ContentFile(base64.b64decode(audio_str), name="voice_message.webm")
            post.audio.save(audio_file.name, audio_file)

        handle_hashtags(post)
        handle_mentions_on_post(post)

        html = render_to_string(
            'components/post_card.html',
            {'post': post, 'reply_form': ReplyForm(), 'request': request}
        )
        return JsonResponse({'ok': True, 'html': html})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    
def filter_jobs_ajax(request):
    """AJAX-Filter für Jobliste nach Skills und Job-Art"""
    skills = request.GET.getlist("skills[]")
    job_type = request.GET.get("job_type")

    jobs = Job.objects.all()

    if job_type:
        jobs = jobs.filter(employment_type=job_type)

    if skills:
        jobs = jobs.filter(required_skills__name__in=skills).distinct()

    html = render_to_string("partials/job_list.html", {"jobs": jobs})
    return JsonResponse({"html": html})


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = profile_user.profile.followers.all()
    following = profile_user.profile.following.all()

    # Prüfen, ob der eingeloggte User diesem Profil folgt
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = profile_user.profile.followers.filter(id=request.user.id).exists()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile_user.profile)
        if form.is_valid():
            form.save()
            # Skills aus Checkboxen speichern
            selected_skill_ids = request.POST.getlist('skills')
            if selected_skill_ids:
                profile_user.profile.skills.set(selected_skill_ids)
            else:
                profile_user.profile.skills.clear()
            return redirect('profile', username=username)
    else:
        form = UserProfileForm(instance=profile_user.profile)

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'followers': followers,
        'following': following,
        'form': form,
        'skills': Skill.objects.all(),
        'all_skills': Skill.objects.all(),
        'all_companies': Company.objects.all(),
        'is_following': is_following, 
    })

# 🔧 COMPANY CREATE
def company_create_view(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            return redirect('profile', username=request.user.username)
    else:
        form = CompanyForm()

    return render(request, 'company_create.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Job, Skill, Company
from .forms import JobForm

@login_required
def job_create_view(request):
    """
    Erstellt einen neuen Job. Nur Benutzer mit Company dürfen Jobs posten.
    Zusätzlich wird automatisch ein Post in der Timeline erzeugt.
    """
    user_companies = Company.objects.filter(owner=request.user)
    all_skills = Skill.objects.all()

    # ⛔ Wenn User keine Company hat → abbrechen
    if not user_companies.exists():
        return render(request, "job_create.html", {
            "error": "Du musst zuerst ein Unternehmen erstellen, bevor du einen Job posten kannst.",
            "skills": all_skills,
            "user_companies": user_companies,
        })

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            company_id = request.POST.get("company")
            if not company_id:
                return render(request, "job_create.html", {
                    "form": form,
                    "skills": all_skills,
                    "user_companies": user_companies,
                    "error": "Bitte wähle ein Unternehmen aus.",
                })

            company = Company.objects.get(id=company_id)

            # 🔹 Job speichern (Ersteller = eingeloggter User)
            job = form.save(commit=False)
            job.company = company
            job.created_by = request.user
            job.save()

            # 🔹 Skills speichern
            selected_skill_ids = request.POST.getlist("skills")
            if selected_skill_ids:
                job.required_skills.set(selected_skill_ids)

            # 🔹 Automatisch einen Post für die Timeline erstellen
            skill_names = [s.name for s in job.required_skills.all()]
            skill_text = ", ".join(skill_names) if skill_names else "Keine Skills angegeben"

            content = (
                f"🧑‍💼 **{job.title}** bei **{company.name}**\n\n"
                f"{job.description}\n\n"
                f"💼 Beschäftigungsart: {job.employment_type}\n"
                f"🛠️ Erforderliche Skills: {skill_text}"
            )

            Post.objects.create(
                user=request.user,
                content=content,
                job=job  # ➕ Verknüpfe Post mit Job
            )

            return redirect("jobs")

    else:
        form = JobForm()

    return render(request, "job_create.html", {
        "form": form,
        "skills": all_skills,
        "user_companies": user_companies,
    })


def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('feed')
        return render(request, 'auth/login.html', {'error': 'Ungültige Zugangsdaten'})
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def signup_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pw = request.POST.get('password')
        if not uname or not pw:
            return render(request, 'auth/signup.html', {'error': 'Bitte Benutzername & Passwort angeben.'})
        if User.objects.filter(username__iexact=uname).exists():
            return render(request, 'auth/signup.html', {'error': 'Benutzername ist bereits vergeben.'})
        user = User.objects.create_user(username=uname, email=email, password=pw)
        login(request, user)
        return redirect('feed')
    return render(request, 'auth/signup.html')


@login_required
def feed(request):
    posts = Post.objects.select_related('user', 'user__profile').prefetch_related('hashtags', 'replies').order_by('-created')[:PAGE_SIZE]
    context = {
        'posts': posts,
        'post_form': PostForm(),
        'reply_form': ReplyForm(),
        'csrf_token': get_token(request),
    }
    return render(request, 'feed.html', context)


@login_required
@require_GET
def api_posts(request):
    offset = int(request.GET.get('offset', 0))
    tag = request.GET.get('tag')
    base_qs = Post.objects.select_related('user', 'user__profile').prefetch_related('hashtags', 'replies').order_by('-created')
    if tag:
        base_qs = base_qs.filter(hashtags__name__iexact=tag)
    posts = list(base_qs[offset:offset+PAGE_SIZE])
    html = ''.join([render_to_string('components/post_card.html', {'post': p, 'reply_form': ReplyForm(), 'request': request}) for p in posts])
    finished = (offset + PAGE_SIZE) >= base_qs.count()
    return JsonResponse({'html': html, 'next_offset': offset + PAGE_SIZE, 'finished': finished})


@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.youtube_id = extract_youtube_id(post.content)
        post.save()
        handle_hashtags(post)
        handle_mentions_on_post(post)
        html = render_to_string('components/post_card.html', {'post': post, 'reply_form': ReplyForm(), 'request': request})
        return JsonResponse({'ok': True, 'html': html})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def create_reply(request):
    post_id = request.POST.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    form = ReplyForm(request.POST)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.user = request.user
        reply.post = post
        reply.save()
        handle_mentions_on_reply(reply)
        if post.user != request.user:
            Notification.objects.create(user=post.user, actor=request.user, post=post, notif_type='reply')
        html = render_to_string('components/reply_item.html', {'reply': reply, 'request': request})
        return JsonResponse({'ok': True, 'html': html, 'reply_count': post.reply_count()})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


PAGE_SIZE = 10


@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.user != request.user:
            Notification.objects.create(user=post.user, actor=request.user, post=post, notif_type='like_post')
    return JsonResponse({'liked': liked, 'count': post.like_count()})


@login_required
@require_GET
def likers_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    names = list(post.post_likes.select_related('user').values_list('user__username', flat=True))
    return JsonResponse({'users': names})


@login_required
@require_POST
def like_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    like, created = ReplyLike.objects.get_or_create(reply=reply, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if reply.user != request.user:
            Notification.objects.create(user=reply.user, actor=request.user, reply=reply, notif_type='like_reply')
    return JsonResponse({'liked': liked, 'count': reply.like_count()})


# 🔧 PROFILE (zweite Variante – mit Skills im Kontext)
@login_required
def profile(request, username):
    user = get_object_or_404(User, username__iexact=username)
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    followers = User.objects.filter(following_set__following=user)
    following = User.objects.filter(followers_set__follower=user)
    posts = Post.objects.filter(user=user).order_by('-created')[:20]

    if request.method == 'POST' and user == request.user:
        form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        if form.is_valid():
            form.save()
            selected_skill_ids = request.POST.getlist('skills')
            if selected_skill_ids:
                user.profile.skills.set(selected_skill_ids)
            else:
                user.profile.skills.clear()
            return redirect('profile', username=user.username)
    else:
        form = ProfileForm(instance=user.profile)

    return render(request, 'profile.html', {
        'profile_user': user,
        'is_following': is_following,
        'followers': followers,
        'following': following,
        'posts': posts,
        'form': form,
        'all_skills': Skill.objects.all(),
        'all_companies': Company.objects.all(),
    })
# 🔧 PROFILE (zweite Variante – mit Skills im Kontext)
@login_required
def edit_profile(request):
    user = request.user  # Eingeloggter Nutzer
    profile = user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            # Skills aktualisieren
            selected_skill_ids = request.POST.getlist('skills')
            if selected_skill_ids:
                profile.skills.set(selected_skill_ids)
            else:
                profile.skills.clear()

            # Company aktualisieren
            company_id = request.POST.get('company')
            if company_id:
                profile.company_id = company_id
            else:
                profile.company = None

            profile.save()
            return redirect('profile', username=user.username)

    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'profile_user': user,
        'form': form,
        'all_skills': Skill.objects.all(),
        'all_companies': Company.objects.all(),
    })

@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username__iexact=username)

    if target == request.user:
        return JsonResponse({"error": "cannot_follow_self"}, status=400)

    rel, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target
    )

    if not created:
        rel.delete()
        is_following = False
    else:
        is_following = True

    follower_count = Follow.objects.filter(following=target).count()

    return JsonResponse({
        "success": True,
        "following": is_following,
        "followers": follower_count
    })

@login_required
def hashtag(request, tag):
    tag = tag.lower()
    return render(request, 'hashtag.html', {'tag': tag})


@login_required
@require_GET
def api_notifications(request):
    notifs = request.user.notifications.select_related('actor', 'post', 'reply')[:20]
    html = render_to_string('notifications_dropdown.html', {'notifications': notifs, 'request': request})
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'html': html, 'unread': unread_count})


@login_required
@require_POST
def notifications_mark_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})


@login_required
@require_POST
def notifications_archive(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})


@login_required
@require_POST
def notifications_clear(request):
    request.user.notifications.all().delete()
    return JsonResponse({'ok': True})


def companies_view(request):
    companies = Company.objects.all()
    return render(request, 'companies.html', {'companies': companies})


def people_view(request):
    users = User.objects.select_related('profile').all()
    return render(request, 'people.html', {'users': users})

def jobs_view(request):
    jobs = Job.objects.all().order_by('-created_at')
    skills = Skill.objects.all()  # ⬅️ NEU: Skills laden
    return render(request, "jobs.html", {"jobs": jobs, "skills": skills})  # ⬅️ skills hinzufügen

@login_required
@require_POST
def job_delete_view(request, job_id):
    """Löscht einen Job, wenn der eingeloggte User ihn erstellt hat."""
    job = get_object_or_404(Job, id=job_id)

    if job.created_by != request.user:
        return JsonResponse({"ok": False, "error": "Keine Berechtigung."}, status=403)

    job.delete()
    return JsonResponse({"ok": True})

def company_detail(request, id):
    company = get_object_or_404(Company, id=id)
    return render(request, 'company_detail.html', {'company': company})


@login_required
def project_create_view(request):
    """
    Erstellt ein neues Projekt (Portfolioeintrag) und erzeugt automatisch
    einen Post in der Timeline mit Titel, Beschreibung, Bild, URL und Skills.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user.profile  # UserProfile als Owner
            project.save()
            form.save_m2m()

            # 🔹 Skills als Text
            skills = project.skills.all()
            skill_text = ", ".join([s.name for s in skills]) if skills else "Keine Skills angegeben"

            # 🔹 Post-Inhalt formatieren
            content = (
                f"🚀 **{project.title}**\n\n"
                f"{project.description}\n\n"
                f"🌐 [Zum Projekt]({project.url})\n\n"
                f"🛠️ Skills: {skill_text}"
            )

            # 🔹 Automatischen Post erzeugen
            Post.objects.create(
                user=request.user,          # ganz normaler User-Post
                content=content,
                image=project.image or None # falls vorhanden, wird das Bild übernommen
            )

            # Weiterleitung bleibt unverändert (Profilseite)
            return redirect('profile', username=request.user.username)

    else:
        form = ProjectForm()

    return render(request, 'project_create.html', {
        'form': form,
        'skills': Skill.objects.all(),
    })

@login_required
@require_POST
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    content = request.POST.get('content', '').strip()
    if not content:
        return HttpResponseBadRequest('Content required')
    image = request.FILES.get('image')
    if image is not None:
        post.image = image
    post.content = content
    post.save()
    # Return simple HTML for updated post snippet if needed
    return JsonResponse({'ok': True, 'id': post.id, 'content': post.content})

@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()
    return JsonResponse({"deleted": True})

@login_required
@require_POST
def repost_post(request, post_id):
    original = get_object_or_404(Post, id=post_id)

    if Post.objects.filter(user=request.user, original_post=original).exists():
        return JsonResponse({'error': 'already_reposted'}, status=400)

    new_post = Post.objects.create(
        user=request.user,
        original_post=original
    )

    # Repost-HTML rendern → FE kann es sofort einsetzen
    html = render_to_string(
        "components/post_card.html",
        {"post": new_post, "request": request}
    )

    return JsonResponse({
        "success": True,
        "post_id": new_post.id,
        "html": html
    })


@login_required
def broadcast(request, room):
    return render(request, "webrtc_live/broadcast.html", {"room": room})

@login_required
def watch(request, room):
    return render(request, "webrtc_live/watch.html", {"room": room})


@login_required
def apply_for_job(request, job_id):
    """
    Wird per AJAX aufgerufen, wenn ein Benutzer auf „Bewerben“ klickt.
    Erstellt eine Bewerbung und sendet eine Notification an den Job-Ersteller.
    """
    job = get_object_or_404(Job, id=job_id)

    # 🔹 Doppelte Bewerbung verhindern
    if job.applicants.filter(id=request.user.id).exists():
        return JsonResponse({"status": "error", "message": "Bereits beworben."})

    # 🔹 Bewerber hinzufügen
    job.applicants.add(request.user)

    # 🔹 Notification nur, wenn der Job-Ersteller existiert und nicht der Bewerber selbst ist
    if job.created_by and job.created_by != request.user:
        Notification.objects.create(
            user=job.created_by,          # Empfänger (Job-Ersteller)
            actor=request.user,           # Bewerber
            notif_type='job_application', # Typ laut NOTIF_TYPES
            job=job
        )

    return JsonResponse({"status": "ok", "message": "Bewerbung gesendet."})
