from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Importiere das Skill Modell, falls es in einer anderen Datei ist
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    availability = models.BooleanField(default=True)  # Verfügbarkeit des Benutzers
    skills = models.ManyToManyField(Skill, related_name='users')  # Verknüpfung zu den Fähigkeiten
    reputation = models.FloatField(default=0.0)  # 🧠 NEU: Pandas-berechnete Reputation

    def __str__(self):
        return self.user.username


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_companies')
    avatar = models.ImageField(upload_to='company_avatars/', blank=True, null=True)  # Avatar für Unternehmen
    
    def __str__(self):
        return self.name
    
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    required_skills = models.ManyToManyField(Skill, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    employment_type = models.CharField(
        max_length=50,
        choices=(
            ('Full-time', 'Full-time'),
            ('Part-time', 'Part-time'),
            ('Contract', 'Contract'),
            ('Internship', 'Internship'),
            ('Working student', 'Working student'),
        ),
        default='Full-time',
    )

    # 🔹 Der Benutzer, der das Job-Angebot erstellt hat (Ersteller des Jobs)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_jobs',
        null=True, blank=True,
    )

    # 🔹 Optional: Liste der Bewerber
    applicants = models.ManyToManyField(
        User,
        related_name='applied_jobs',
        blank=True
    )

    def __str__(self):
        return f"{self.title} bei {self.company.name}"

    def has_applied(self, user):
        """Hilfsfunktion: Prüfen, ob der Benutzer sich schon beworben hat."""
        return self.applicants.filter(id=user.id).exists()

    
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} -> {self.following}"

class Hashtag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"#{self.name}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    hashtags = models.ManyToManyField(Hashtag, through='PostHashtag', blank=True)
    youtube_id = models.CharField(max_length=32, blank=True, default='')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    original_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reposts')

    def repost_count(self):
        return self.reposts.count()

    def like_count(self):
        return self.post_likes.count()

    def reply_count(self):
        return self.replies.count()

    def __str__(self):
        return f"Post({self.id}) by {self.user.username}"

class PostHashtag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_hashtags')
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='hashtag_posts')

    class Meta:
        unique_together = ('post', 'hashtag')

class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created = models.DateTimeField(default=timezone.now)

    def like_count(self):
        return self.reply_likes.count()

    def __str__(self):
        return f"Reply({self.id}) to Post({self.post_id})"

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post_likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

class ReplyLike(models.Model):
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='reply_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reply_likes')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reply', 'user')

class Mention(models.Model):
    mentioned_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='mentions', null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='mentions', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

NOTIF_TYPES = [
    ('follow', 'Follow'),
    ('unfollow', 'Unfollow'),
    ('mention_post', 'Mention in Post'),
    ('mention_reply', 'Mention in Reply'),
    ('like_post', 'Like Post'),
    ('like_reply', 'Like Reply'),
    ('reply', 'Reply'),
    ('job_application', 'Job Application'),
]

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')  # Empfänger
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actor_notifications')
    notif_type = models.CharField(max_length=32, choices=NOTIF_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True)

    # 🔹 Ergänzung für Bewerbungen
    job = models.ForeignKey("Job", on_delete=models.CASCADE, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.notif_type} -> {self.user} (by {self.actor})"

class Project(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

