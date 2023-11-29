from django.urls import path, include
from rest_framework import routers
from .views import S3Upload, DownloadS3File, IsUploaded
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('uploads/', S3Upload.as_view(), name='file-uploads'),
    path('download/<str:file_name>', DownloadS3File.as_view(), name='file-downlaods'),
    path('isuploaded/<str:file_name>', IsUploaded.as_view(), name='client-uploaded-or-not')

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)