from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Connection

User = get_user_model()

def _existing_between(a, b):
    return Connection.objects.filter(Q(from_user=a, to_user=b) | Q(from_user=b, to_user=a)).first()

@login_required
def connections_list(request):
    links = Connection.objects.filter(
        Q(from_user=request.user, status=Connection.ACCEPTED) |
        Q(to_user=request.user, status=Connection.ACCEPTED)
    ).select_related('from_user','to_user').order_by('-created_at')
    people = [(c.to_user if c.from_user_id == request.user.id else c.from_user, c) for c in links]
    return render(request, 'connections_list.html', {'people': people})

@login_required
def connection_requests(request):
    incoming = Connection.objects.filter(to_user=request.user, status=Connection.PENDING).select_related('from_user')
    return render(request, 'connections_requests.html', {'incoming': incoming})

@login_required
def send_request(request, username):
    if request.method != 'POST':
        messages.error(request, 'Invalid method.')
        return redirect('profile_detail', username=username)
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, 'You cannot connect with yourself.')
        return redirect('profile_detail', username=username)
    existing = _existing_between(request.user, target)
    if existing:
        if existing.status == Connection.PENDING:
            messages.info(request, 'Request already pending.')
        elif existing.status == Connection.ACCEPTED:
            messages.info(request, 'You are already connected.')
        else:
            existing.delete()
            Connection.objects.create(from_user=request.user, to_user=target, status=Connection.PENDING)
            messages.success(request, 'Connection request sent again.')
    else:
        Connection.objects.create(from_user=request.user, to_user=target, status=Connection.PENDING)
        messages.success(request, 'Connection request sent.')
    return redirect('profile_detail', username=target.username)

@login_required
def accept_request(request, id):
    if request.method != 'POST':
        messages.error(request, 'Invalid method.')
        return redirect('connection_requests')
    conn = get_object_or_404(Connection, id=id, to_user=request.user, status=Connection.PENDING)
    conn.status = Connection.ACCEPTED
    conn.save(update_fields=['status'])
    messages.success(request, f'Connected with {conn.from_user.get_full_name() or conn.from_user.username}.')
    return redirect('connection_requests')

@login_required
def reject_request(request, id):
    if request.method != 'POST':
        messages.error(request, 'Invalid method.')
        return redirect('connection_requests')
    conn = get_object_or_404(Connection, id=id, to_user=request.user, status=Connection.PENDING)
    conn.status = Connection.REJECTED
    conn.save(update_fields=['status'])
    messages.info(request, 'Request rejected.')
    return redirect('connection_requests')

@login_required
def remove_connection(request, username):
    if request.method != 'POST':
        messages.error(request, 'Invalid method.')
        return redirect('connections_list')
    from django.db.models import Q
    other = get_object_or_404(User, username=username)
    conn = _existing_between(request.user, other)
    if not conn or conn.status != Connection.ACCEPTED:
        messages.error(request, 'No active connection.')
        return redirect('profile_detail', username=other.username)
    conn.delete()
    messages.success(request, f'Removed connection with {other.get_full_name() or other.username}.')
    return redirect('profile_detail', username=other.username)
