from django.urls import path
from . import views

app_name = 'fichas'

urlpatterns = [
    path('', views.home_fichas_view, name='home'),
    path('usuario/', views.fichas_usuario_view, name='fichas_usuario'),
    path('criar/', views.criar_ficha_view, name='criar_ficha'),
    path('limpar/', views.limpar_fichas_view, name='limpar_fichas'),
    
    path('<int:ficha_id>/<slug:categoria>/criar/', views.criar_view, name='criar'),
    path('<int:ficha_id>/<slug:categoria>/', views.ler_view, name='ler'),
    path('<int:categoria_id>/<slug:categoria>/salvar/', views.salvar_view, name='salvar'),
    path('<int:ficha_id>/<str:categoria>/salvar/imagem/', views.salvar_imagem_view, name='salvar_imagem'),
    path('<int:categoria_id>/<slug:categoria>/excluir/', views.excluir_view, name='excluir'),

    path('<int:ficha_id>/ficha/exportar/', views.exportar_view, name='exportar_ficha'),
    path('<int:ficha_id>/ficha/importar/', views.importar_view, name='importar_ficha'),
]