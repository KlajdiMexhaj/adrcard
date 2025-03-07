from . import views
from django.urls import path

urlpatterns = [
    path("",views.home,name="home"),
    path('generate_qr/<uuid:guid>/', views.generate_qr_code, name='generate_qr_code'),
    path('<uuid:guid>/', views.login_view, name='login'),
    path("propozimet/",views.propozimet,name="propozimet"),
    path("statuti/",views.statuti,name="statuti"),
    path("programi/",views.programi,name="programi"),
    path("propozimet-per-aprovim/",views.propozimet1,name="propozimet1"),
    path("propozimet-per-votim/",views.propozimet2,name="propozimet2"),
    path("propozimet-e-votuara/",views.propozimet3,name="propozimet3"),
    path("axhenda-e-eventeve/",views.axhendaeventeve,name="axhendaeventeve"),
    path("kandidat-per-deputet/",views.kandidatdeputet,name="kandidatdeputet"),
    path("organigrama-e-partisë/",views.organigrama,name="organigrama"),
    path("asambleja/", views.asambleja, name="asambleja"),
    path("sekretaria/",views.sekretaria,name="sekretaria"),
    path("koordinatori/",views.koordinatori,name="koordinatori"),
    path("komunikime-zyrtare/",views.komunikimezyrtare,name="komunikimezyrtare"),
    path('print-card/<str:guid>/', views.printcard, name='printcard'),
]