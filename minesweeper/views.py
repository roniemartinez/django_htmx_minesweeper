import random
from typing import Any

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "minesweeper/index.html"

    def get(self, request, *args, **kwargs):
        test = cache.get("test")
        if test is None:
            cache.set("test", "hello")  # TODO: generate new board
        return super().get(request, *args, **kwargs)


class ClickedView(View):
    def post(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        print(cache.get("test"))  # TODO: retrieve board and update grid (revealed, marked)
        trigger = request.headers.get("Hx-Trigger", "click")
        if trigger == "contextmenu":
            return render(
                request=request,
                template_name="minesweeper/flag.html",
                context={
                    "x": kwargs["x"],
                    "y": kwargs["y"],
                },
            )
        return render(
            request=request,
            template_name="minesweeper/revealed.html",
            context={
                "image": random.choice(
                    (
                        "mine.svg",
                        "blank.svg",
                        "numeric-1.svg",
                        "numeric-2.svg",
                        "numeric-3.svg",
                        "numeric-4.svg",
                        "numeric-5.svg",
                        "numeric-6.svg",
                        "numeric-7.svg",
                        "numeric-8.svg",
                    )
                )
            },
        )
