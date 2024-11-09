# custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def is_sent_by_user(discussion, user):
    return discussion.sent_by == user