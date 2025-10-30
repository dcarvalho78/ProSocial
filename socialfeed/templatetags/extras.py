from django import template
import re
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

MENTION_RE = re.compile(r'@(\w+)')
HASHTAG_RE = re.compile(r'#(\w+)')
YOUTUBE_RE = re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w\-]{11})')

@register.filter
def linkify(value):
    text = value or ''
    text = re.sub(MENTION_RE, lambda m: f'<a href="{reverse("profile", args=[m.group(1)])}">@{m.group(1)}</a>', text)
    text = re.sub(HASHTAG_RE, lambda m: f'<a class="badge bg-gradient" href="{reverse("hashtag", args=[m.group(1)])}">#{m.group(1)}</a>', text)
    # Plain URLs
    text = re.sub(r'(https?://\\S+)', r'<a href="\\1" target="_blank">\\1</a>', text)
    return mark_safe(text)

@register.filter
def youtube_embed(content):
    text = content or ''
    m = YOUTUBE_RE.search(text)
    if not m:
        return ''
    vid = m.group(1)
    iframe = f'''<div class="ratio ratio-16x9 mt-2">
<iframe src="https://www.youtube.com/embed/{vid}" title="YouTube video" allowfullscreen></iframe>
</div>'''
    return mark_safe(iframe)
