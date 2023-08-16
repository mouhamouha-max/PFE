from django.urls import path
from . import views
from .views import AnalysisResultsView

urlpatterns = [
    path('upload/', views.upload_pcap_file, name='upload_pcap_file'),
    path('filter/', views.filter_pcap, name='filter_pcap'),
    path('analyze_pcap/', views.analyze_pcap, name='analyze_pcap'),
    path('api/analysis/', AnalysisResultsView.as_view(), name='api-analysis'),
]
