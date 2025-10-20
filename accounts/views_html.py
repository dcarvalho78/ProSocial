from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from connections.models import Connection
from .forms import SignUpForm, ProfileForm

User = get_user_model()


# -----------------------------
#   SIGN UP
# -----------------------------
def signup(request):
    """User registration with automatic login"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Sign-up successful. You are now logged in.')
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# -----------------------------
#   PROFILE DETAIL
# -----------------------------
def profile_detail(request, username):
    """Public profile page with connection status"""
    user_obj = get_object_or_404(User, username=username)

    def _state(viewer, other):
        """Determine relationship state between viewer and profile owner."""
        if not viewer.is_authenticated or viewer == other:
            return None
        c = Connection.objects.filter(
            Q(from_user=viewer, to_user=other) | Q(from_user=other, to_user=viewer)
        ).first()
        if not c:
            return 'none'
        if c.status == Connection.ACCEPTED:
            return 'connected'
        if c.status == Connection.PENDING and c.from_user_id == viewer.id:
            return 'pending_out'
        if c.status == Connection.PENDING and c.to_user_id == viewer.id:
            return 'pending_in'
        return 'none'

    connection_state = _state(request.user, user_obj)

    return render(request, 'accounts/profile_detail.html', {
        'user_obj': user_obj,
        'skills': user_obj.skills.all(),
        'company': getattr(user_obj, 'company', None),
        'connection_state': connection_state,
    })


# -----------------------------
#   PROFILE EDIT
# -----------------------------
@login_required
def profile_edit(request, username):
    """Edit own profile — allows optional company, skills, and availability"""
    if request.user.username != username and not request.user.is_staff:
        messages.error(request, 'You can only edit your own profile.')
        return redirect('profile_detail', username=username)

    user_obj = get_object_or_404(User, username=username)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            form.save_m2m()  # For many-to-many fields like skills
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_detail', username=username)
    else:
        form = ProfileForm(instance=user_obj)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'user_obj': user_obj
    })
