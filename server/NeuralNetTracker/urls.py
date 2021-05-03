"""NeuralNetTracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="Frontpage"),
    path('login/', views.login, name="Authentication"),
    path('register/', views.signup, name="AccountCreation"),
    path('simulations/', views.simulations, name="SimulationList"),
    path('simulations/create/', views.simulation_create, name="SimulationCreate"),
    path('simulations/<int:id>/', views.simulation_info, name="SimulationInfo"),
    path('api/simulations/', views.simulation_view, name="Simulations"),
    path('api/simulations/<int:id>', views.get_simulation, name="GetSimulation"),
    path('api/simulations/<int:id>/<str:command>', views.command_simulation, name="CommandSimulation"),
]
