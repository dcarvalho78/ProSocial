from connections.models import Connection

def pending_requests_count(request):
    if request.user.is_authenticated:
        return {
            'pending_requests_count': Connection.objects.filter(
                to_user=request.user,
                status='P'
            ).count()
        }
    return {'pending_requests_count': 0}
