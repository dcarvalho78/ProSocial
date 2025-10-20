from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from posts.forms import PostForm
from posts.models import Post
from jobs.forms import JobForm
from jobs.models import Job
from companies.forms import CompanyForm
from companies.models import Company

def _user_is_company_admin(user, company):
    return user.is_authenticated and company.admins.filter(id=user.id).exists()

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            company = form.cleaned_data.get('company')
            if company and not _user_is_company_admin(request.user, company):
                messages.error(request, 'You are not an admin of that company page.')
                return render(request, 'post_form.html', {'form': form})
            post.save()
            messages.success(request, 'Post published.')
            return redirect('feed')
    else:
        form = PostForm(user=request.user)
    return render(request, 'post_form.html', {'form': form})

@login_required
def post_edit(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post, user=request.user)
        if form.is_valid():
            company = form.cleaned_data.get('company')
            if company and not _user_is_company_admin(request.user, company):
                messages.error(request, 'You are not an admin of that company page.')
                return render(request, 'post_form.html', {'form': form, 'post': post})
            form.save()
            messages.success(request, 'Post updated.')
            return redirect('feed')
    else:
        form = PostForm(instance=post, user=request.user)
    return render(request, 'post_form.html', {'form': form, 'post': post})

@login_required
def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            company.admins.add(request.user)
            messages.success(request, 'Company page created (you were added as admin).')
            return redirect('company_detail', slug=company.slug)
    else:
        form = CompanyForm()
    return render(request, 'company_form.html', {'form': form})

@login_required
def company_edit(request, slug):
    company = get_object_or_404(Company, slug=slug)
    if not _user_is_company_admin(request.user, company):
        messages.error(request, 'Only company admins can edit this page.')
        return redirect('company_detail', slug=slug)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company updated.')
            return redirect('company_detail', slug=slug)
    else:
        form = CompanyForm(instance=company)
    return render(request, 'company_form.html', {'form': form, 'company': company})

@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST, user=request.user)
        if form.is_valid():
            company = form.cleaned_data['company']
            if not _user_is_company_admin(request.user, company):
                messages.error(request, 'Only company admins can post jobs for that company.')
                return render(request, 'job_form.html', {'form': form})
            job = form.save()
            messages.success(request, 'Job published.')
            return redirect('jobs_list')
    else:
        form = JobForm(user=request.user)
    return render(request, 'job_form.html', {'form': form})

@login_required
def job_edit(request, id):
    job = get_object_or_404(Job, id=id)
    if not _user_is_company_admin(request.user, job.company):
        messages.error(request, 'Only company admins can edit this job.')
        return redirect('job_detail', id=id)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated.')
            return redirect('job_detail', id=id)
    else:
        form = JobForm(instance=job, user=request.user)
    return render(request, 'job_form.html', {'form': form, 'job': job})
