""" Параметры urls и др для тестирования"""
urls_names_templates_to_check = [
    {
        'url': '/',
        'name': 'posts:index',
        'template': 'posts/index.html',
        'access': 'all',
        'reverse_kwargs': {},
    },
    {
        'url': '/group/test-slug/',
        'name': 'posts:group_list',
        'template': 'posts/group_list.html',
        'access': 'all',
        'reverse_kwargs': {'slug': 'test-slug'},
    },
    {
        'url': '/profile/auth/',
        'name': 'posts:profile',
        'template': 'posts/profile.html',
        'access': 'all',
        'reverse_kwargs': {'username': 'auth'},
    },
    {
        'url': '/posts/1/',
        'name': 'posts:post_detail',
        'template': 'posts/post_detail.html',
        'access': 'all',
        'reverse_kwargs': {'post_id': '1'},
    },
    {
        'url': '/posts/1/edit/',
        'name': 'posts:post_edit',
        'template': 'posts/create_post.html',
        'access': 'author',
        'reverse_kwargs': {'post_id': '1'},
    },
    {
        'url': '/create/',
        'name': 'posts:post_create',
        'template': 'posts/create_post.html',
        'access': 'authorized',
        'reverse_kwargs': {},
    },
]
