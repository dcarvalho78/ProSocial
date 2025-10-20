from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from accounts.models import Skill
from companies.models import Company
from jobs.models import Job
from posts.models import Post
from connections.models import Connection

User = get_user_model()

SKILL_POOL = [
    'Python','Django','REST','JavaScript','React','TypeScript','AWS','Docker','Kubernetes','SQL',
    'PostgreSQL','Redis','CI/CD','Machine Learning','Data Analysis','HTML','CSS','UX','Product Management',
    'Go','Rust','Node.js','GraphQL','GCP','Azure','Tailwind','Bootstrap','Linux','Terraform'
]

class Command(BaseCommand):
    help = "Seed database with users (with skills & availability), companies, jobs, posts, and connections."

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=20)
        parser.add_argument('--companies', type=int, default=8)
        parser.add_argument('--posts', type=int, default=40)
        parser.add_argument('--jobs', type=int, default=20)
        parser.add_argument('--connections', type=int, default=50)
        parser.add_argument('--reset', action='store_true', help='Purge existing data before seeding')

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker('en_US')

        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting data...'))
            Connection.objects.all().delete()
            Post.objects.all().delete()
            Job.objects.all().delete()
            Company.objects.all().delete()
            # Keep superuser if exists
            User.objects.filter(is_superuser=False).delete()
            Skill.objects.all().delete()

        # Skills
        skills = []
        for name in SKILL_POOL:
            skills.append(Skill.objects.create(name=name))
        self.stdout.write(self.style.SUCCESS(f"Skills: {len(skills)}"))

        # Users
        users = list(User.objects.filter(is_superuser=False))
        needed = options['users'] - len(users)
        for _ in range(max(0, needed)):
            first = fake.first_name()
            last = fake.last_name()
            username = slugify(f"{first}.{last}{random.randint(1,9999)}")
            u = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="password123",
                first_name=first,
                last_name=last,
                headline=fake.job(),
                bio=fake.paragraph(nb_sentences=3),
                location=fake.city(),
                is_available_for_hire=random.choice([True, False, False]),
            )
            # availability details
            if u.is_available_for_hire and random.random() < 0.6:
                u.availability_note = random.choice(["Immediate", "Part-time only", "Remote preferred", "Open to contracts"])
            u.save()
            # assign skills
            u.skills.add(*random.sample(skills, k=random.randint(2, 7)))
            users.append(u)
        self.stdout.write(self.style.SUCCESS(f"Users: {len(users)}"))

        # Companies
        companies = list(Company.objects.all())
        needed_c = options['companies'] - len(companies)
        for _ in range(max(0, needed_c)):
            name = fake.company()
            slug = slugify(name)
            # ensure slug uniqueness
            uniq = f"{slug}-{random.randint(100,999)}"
            c = Company.objects.create(
                name=name,
                slug=uniq,
                description=fake.paragraph(nb_sentences=5),
                website=f"https://{slug}.example.com",
                industry=random.choice(['Software','FinTech','AI','Consulting','E-commerce','Media','HealthTech']),
                location=fake.city(),
            )
            admins = random.sample(users, k=min(2, len(users)))
            c.admins.add(*admins)
            employees = random.sample(users, k=min(random.randint(3,10), len(users)))
            c.employees.add(*employees)
            for a in admins:
                a.is_company_admin = True
                a.save(update_fields=['is_company_admin'])
            companies.append(c)
        self.stdout.write(self.style.SUCCESS(f"Companies: {len(companies)}"))

        # Jobs
        jobs = list(Job.objects.all())
        needed_j = options['jobs'] - len(jobs)
        for _ in range(max(0, needed_j)):
            comp = random.choice(companies)
            title = fake.job()
            j = Job.objects.create(
                company=comp,
                title=title,
                description="\n\n".join(fake.paragraphs(nb=3)),
                location=fake.city(),
                employment_type=random.choice([c for c,_ in Job.EMPLOYMENT_TYPES]),
                salary_min=random.choice([None, 40000, 50000, 60000]),
                salary_max=random.choice([None, 70000, 80000, 90000, 100000]),
            )
            jobs.append(j)
        self.stdout.write(self.style.SUCCESS(f"Jobs: {len(jobs)}"))

        # Posts
        posts = list(Post.objects.all())
        needed_p = options['posts'] - len(posts)
        for _ in range(max(0, needed_p)):
            if random.random() < 0.45 and companies:
                comp = random.choice(companies)
                author = random.choice(list(comp.admins.all()) or users)
                p = Post.objects.create(
                    author=author,
                    company=comp,
                    content=fake.sentence(nb_words=14)
                )
            else:
                author = random.choice(users)
                p = Post.objects.create(
                    author=author,
                    content=fake.sentence(nb_words=16)
                )
            posts.append(p)
        self.stdout.write(self.style.SUCCESS(f"Posts: {len(posts)}"))

        # Connections
        existing = set((c.from_user_id, c.to_user_id) for c in Connection.objects.all())
        created = 0
        target = options['connections']
        attempts = 0
        max_attempts = target * 10
        while created < target and attempts < max_attempts and len(users) >= 2:
            a, b = random.sample(users, 2)
            if (a.id, b.id) in existing or (b.id, a.id) in existing:
                attempts += 1
                continue
            status = random.choices([Connection.PENDING, Connection.ACCEPTED, Connection.REJECTED], weights=[1,3,1])[0]
            Connection.objects.create(from_user=a, to_user=b, status=status)
            existing.add((a.id, b.id))
            created += 1
            attempts += 1
        self.stdout.write(self.style.SUCCESS(f"Connections created: {created}"))
        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
