from django.urls import path
from . import views

urlpatterns = [
    path('discussion/<int:code>', views.discussion, name='discussion'),
    path('send/<int:code>/<str:email>', views.send, name='send'),
    path('message/<int:code>/<str:email>', views.send_fac, name='send_fac'),
]