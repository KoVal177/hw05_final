from django.conf import settings
from django.core.paginator import Paginator


def paginate(post_list, page_number):
    """Returns page for paginator based on list of posts and page number"""
    return Paginator(post_list, settings.POSTS_PER_PAGE).get_page(page_number)
