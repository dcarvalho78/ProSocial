from django.shortcuts import render, get_object_or_404
from posts.models import Post
from companies.models import Company
from jobs.models import Job
from accounts.models import User

def home(request):
    posts = Post.objects.select_related('author','company').order_by('-created_at')[:10]
    companies = Company.objects.order_by('name')[:8]
    return render(request, 'home.html', {'posts': posts, 'companies': companies})

def feed(request):
    posts = Post.objects.select_related('author','company').order_by('-created_at')[:50]
    return render(request, 'feed.html', {'posts': posts})

def companies_list(request):
    companies = Company.objects.order_by('name')[:100]
    return render(request, 'companies_list.html', {'companies': companies})

def company_detail(request, slug):
    company = get_object_or_404(Company, slug=slug)
    posts = company.posts.select_related('author','company').order_by('-created_at')[:30]
    jobs = company.jobs.order_by('-created_at')[:30]
    employees = company.employees.all()[:60]
    return render(request, 'company_detail.html', {'company': company, 'posts': posts, 'jobs': jobs, 'employees': employees})

def jobs_list(request):
    jobs = Job.objects.select_related('company').order_by('-created_at')[:100]
    return render(request, 'jobs_list.html', {'jobs': jobs})

def job_detail(request, id):
    job = get_object_or_404(Job.objects.select_related('company'), id=id)
    return render(request, 'job_detail.html', {'job': job})

def users_list(request):
    users = User.objects.order_by('id').prefetch_related('skills')[:100]
    return render(request, 'users_list.html', {'users': users})
