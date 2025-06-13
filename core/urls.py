from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pagamentos, name='listar_pagamentos'),
    path('adicionar/', views.adicionar_pagamento, name='adicionar_pagamento'),
    path('register/', views.register, name='register'),
]