from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from socialfeed.models import (
    Skill, UserProfile, Company, Job, Follow,
    Hashtag, Post, PostHashtag, Reply, PostLike
)
from faker import Faker
from random import choice, sample, randint
from django.db import transaction


class Command(BaseCommand):
    help = "Erzeugt vollständige Testdaten für proSocial (Users, Skills, Companies, Jobs, Posts, Hashtags, Follows, Likes, Replies)"

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()

        self.stdout.write(self.style.WARNING("🧹 Lösche alte Testdaten..."))

        # Löschreihenfolge (Foreign Keys beachten!)
        PostLike.objects.all().delete()
        Reply.objects.all().delete()
        PostHashtag.objects.all().delete()
        Post.objects.all().delete()
        Follow.objects.all().delete()
        Job.objects.all().delete()
        Company.objects.all().delete()
        UserProfile.objects.all().delete()
        Skill.objects.all().delete()
        Hashtag.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        self.stdout.write(self.style.SUCCESS("✅ Alte Daten sauber gelöscht."))

        # === SKILLS ===
        skills = [Skill.objects.create(name=fake.unique.word()) for _ in range(30)]
        self.stdout.write(self.style.SUCCESS("✅ 30 Skills erstellt."))

        # === USERS & PROFILE ===
        users = []
        for _ in range(300):
            username = fake.user_name()
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password="test1234"
            )
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "bio": fake.sentence(nb_words=15),
                    "availability": choice([True, False]),
                },
            )
            profile.skills.add(*sample(skills, randint(1, 5)))
            users.append(user)

        self.stdout.write(self.style.SUCCESS("✅ 300 User + Profile erstellt."))

        # === COMPANIES ===
        companies = []
        for _ in range(50):
            company = Company.objects.create(
                name=fake.company(),
                description=fake.text(max_nb_chars=300),
                owner=choice(users)
            )
            companies.append(company)
        self.stdout.write(self.style.SUCCESS("✅ 50 Companies erstellt."))

        # === JOBS ===
        jobs = []
        for _ in range(100):
            job = Job.objects.create(
                title=fake.job(),
                description=fake.text(max_nb_chars=400),
                company=choice(companies),
                employment_type=choice([
                    "Full-time", "Part-time", "Contract", "Internship", "Working student"
                ])
            )
            job.required_skills.add(*sample(skills, randint(1, 5)))
            jobs.append(job)
        self.stdout.write(self.style.SUCCESS("✅ 100 Jobs erstellt."))

        # === HASHTAGS ===
        hashtags = [Hashtag.objects.create(name=fake.unique.word().lower()) for _ in range(50)]
        self.stdout.write(self.style.SUCCESS("✅ 50 Hashtags erstellt."))

        # === POSTS ===
        posts = []
        for user in users:
            for _ in range(randint(1, 4)):
                post = Post.objects.create(
                    user=user,
                    content=fake.text(max_nb_chars=200)
                )
                posts.append(post)

                # Hashtags (1–3)
                tag_selection = sample(hashtags, k=min(3, len(hashtags)))
                for tag in tag_selection:
                    PostHashtag.objects.get_or_create(post=post, hashtag=tag)

        self.stdout.write(self.style.SUCCESS(f"✅ {len(posts)} Posts erstellt."))

        # === REPLIES ===
        for _ in range(300):
            Reply.objects.create(
                post=choice(posts),
                user=choice(users),
                content=fake.sentence(nb_words=randint(5, 20))
            )
        self.stdout.write(self.style.SUCCESS("✅ 300 Replies erstellt."))

        # === LIKES ===
        for _ in range(500):
            PostLike.objects.get_or_create(
                post=choice(posts),
                user=choice(users)
            )
        self.stdout.write(self.style.SUCCESS("✅ 500 PostLikes erstellt."))

        # === FOLLOWS ===
        for _ in range(1000):
            follower = choice(users)
            following = choice(users)
            if follower != following:
                Follow.objects.get_or_create(follower=follower, following=following)
        self.stdout.write(self.style.SUCCESS("✅ 1000 Follow-Beziehungen erstellt."))

        self.stdout.write(self.style.SUCCESS("🎉 Alle Testdaten erfolgreich generiert!"))
