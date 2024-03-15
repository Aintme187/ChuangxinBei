"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from backend import settings
from backend.views import attack, stop, get_csrf_token, get_status, generate_attack_image, predict_poisoned_image

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('get_csrf_token/', get_csrf_token),
                  path('attack/', attack),
                  path('stop/', stop),
                  path('get_status/', get_status),  # 新增状态获取url
                  path('attack_backdoor/', generate_attack_image),
                  path('predict/', predict_poisoned_image)
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
