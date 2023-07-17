from django.urls import path
from minesweeper import views

app_name = "minesweeper"


urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("restart/", views.RestartView.as_view(), name="restart"),
    path("clicked/<int:x>/<int:y>/", views.ClickedView.as_view(), name="clicked"),
]
