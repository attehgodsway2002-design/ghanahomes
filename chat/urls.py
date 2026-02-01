from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('start/<uuid:property_id>/', views.start_chat, name='start_chat'),
    path('room/<int:room_id>/send/', views.send_message, name='send_message'),
]