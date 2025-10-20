This is a drop-in templates pack for your Django project (Bootstrap 5).
It includes LinkedIn-style Connections UI and Bootstrap-styled forms.

HOW TO INSTALL
1) Backup your current templates/ folder.
2) Copy all files from this zip into your project's templates/ folder.
3) Ensure in core/urls.py you have:
   path('connections/', include('connections.urls_html'))

4) Make sure the profile view passes 'connection_state' for the viewed profile user.
   Example (in your profile_detail view):
   --------------------------------------------------
   from django.db.models import Q
   from connections.models import Connection

   def _state(viewer, other):
       if not viewer.is_authenticated or viewer == other:
           return None
       qs = Connection.objects.filter(Q(from_user=viewer, to_user=other) | Q(from_user=other, to_user=viewer))
       c = qs.first()
       if not c:
           return 'none'
       if c.status == Connection.ACCEPTED:
           return 'connected'
       if c.status == Connection.PENDING and c.from_user_id == viewer.id:
           return 'pending_out'
       if c.status == Connection.PENDING and c.to_user_id == viewer.id:
           return 'pending_in'
       return 'none'

   user_obj = get_object_or_404(User, username=username)
   connection_state = _state(request.user, user_obj)
   return render(request, 'profile_detail.html', {'user_obj': user_obj, 'connection_state': connection_state})
   --------------------------------------------------

5) Logout button is POST-based (recommended). Ensure /logout/ accepts POST (default Django auth view).

FORMS
All forms use Bootstrap 5 classes. To support the pipe filter add_class used in the templates,
add a simple template filter or install django-widget-tweaks.
Example filter (templatetags/form_extras.py):
--------------------------------------------------
from django import template
register = template.Library()
@register.filter
def add_class(field, css):
    return field.as_widget(attrs={**field.field.widget.attrs, 'class': (field.field.widget.attrs.get('class','') + ' ' + css).strip()})
--------------------------------------------------
Then load it atop templates where needed: {% load form_extras %}

