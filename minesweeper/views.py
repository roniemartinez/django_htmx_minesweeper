import random
from dataclasses import dataclass
from typing import Any

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import RedirectView, TemplateView


@dataclass
class Item:
    is_mine: bool
    count: int = 0
    is_revealed: bool = False
    is_flagged: bool = False


class HomeView(TemplateView):
    template_name = "minesweeper/index.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> TemplateResponse:
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
        return super().get(request, *args, board=board, **kwargs)


class RestartView(RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str:
        cache.delete("board")
        return reverse("minesweeper:home")


class ClickedView(View):
    def post(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        board: list[list[Item]] = cache.get("board")

        trigger = request.headers.get("Hx-Trigger", "click")

        x = kwargs["x"]
        y = kwargs["y"]

        if trigger == "contextmenu":
            board[x][y].is_flagged = not board[x][y].is_flagged
        else:
            board[x][y].is_revealed = True

            if not board[x][y].is_mine and board[x][y].count == 0:
                board = self.reveal_neighbors(board, x, y)

        cache.set("board", board)

        return render(request=request, template_name="minesweeper/board.html", context={"board": board})

    def reveal_neighbors(self, board: list[list[Item]], x: int, y: int) -> list[list[Item]]:
        to_reveal: list[tuple[int, int]] = []
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
                if not board[neighbor_x][neighbor_y].is_revealed:
                    board[neighbor_x][neighbor_y].is_revealed = True
                    if board[neighbor_x][neighbor_y].count == 0:
                        to_reveal.append((neighbor_x, neighbor_y))
            except IndexError:
                pass

        for neighbor_x, neighbor_y in to_reveal:
            board = self.reveal_neighbors(board, neighbor_x, neighbor_y)
        return board
