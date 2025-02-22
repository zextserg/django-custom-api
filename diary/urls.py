from django.urls import path
from diary import views 

get_apis = [path(f"{v['func']}/", getattr(views, v['func'])) for k,v in views.API_SCHEMA['all_get_apis'].items() if 'func' in v and hasattr(views, v['func'])]
post_apis = [path(f"{v['func']}/", getattr(views, v['func'])) for k,v in views.API_SCHEMA['all_post_apis'].items() if 'func' in v and hasattr(views, v['func'])]

urlpatterns = [
    path("", views.get_all_apis),
] + get_apis + post_apis