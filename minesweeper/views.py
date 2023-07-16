import random
from dataclasses import dataclass
from typing import Any

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView


@dataclass
class Item:
    is_mine: bool
    count: int = 0
    is_revealed: bool = False


class HomeView(TemplateView):
    template_name = "minesweeper/index.html"

    def get(self, request, *args, **kwargs):
        board = cache.get("board")
        if board is None:
            # Generate board
            max_width = 10
            coordinates = [(x, y) for x in range(max_width) for y in range(max_width)]
            mines = random.sample(coordinates, k=max_width)
            board = [[Item(is_mine=(x, y) in mines) for x in range(max_width)] for y in range(max_width)]
            for y in range(max_width):
                for x in range(max_width):
                    if board[x][y].is_mine is True:
                        continue

                    count = 0

                    for neighbor_x, neighbor_y in [
                        (x - 1, y - 1),
                        (x - 1, y),
                        (x - 1, y + 1),
                        (x, y - 1),
                        (x, y + 1),
                        (x + 1, y - 1),
                        (x + 1, y),
                        (x + 1, y + 1),
                    ]:
                        if neighbor_x < 0 or neighbor_y < 0:
                            continue
                        try:
                            count += board[neighbor_x][neighbor_y].is_mine is True
                        except IndexError:
                            pass

                    board[x][y].count = count
            cache.set("board", board)
        return super().get(request, *args, **kwargs)


class ClickedView(View):
    def post(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        item: Item = cache.get("board")[kwargs["x"]][kwargs["y"]]

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

        image = "blank.svg"
        if item.is_mine:
            image = "mine.svg"
        if item.count > 0:
            image = f"numeric-{item.count}.svg"
        return render(
            request=request,
            template_name="minesweeper/revealed.html",
            context={"image": image},
        )
