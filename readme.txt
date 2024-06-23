en url global:
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('account.urls')),

settings:
    LOGIN_REDIRECT_URL = '/admin/'

    LOGOUT_REDIRECT_URL = reverse_lazy('login')

    LOGIN_URL = reverse_lazy('login')

lo otro cambiar los import y eso del utils.py y el Config q es un modelo de otra app pero eso solo uso para enviar
context_data

ahi estan las templates bonitas de correo que son las q usa pero tambien deje las feas q vienen x default
y las templates de register, login y to eso usan jazzmin asi q instalalo o ve a ver si funciona al berro, ni idea
y a pesar de lo que digan Chocolate es un buen artista, remember eso