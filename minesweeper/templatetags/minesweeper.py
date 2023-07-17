from django import template
from django.templatetags.static import static
from minesweeper.views import Item

register = template.Library()


@register.filter(name="svg")
def svg(item: Item) -> str:
    if item.is_flagged:
        return static("minesweeper/img/flag.svg")
    elif item.is_revealed and item.is_mine:
        return static("minesweeper/img/mine.svg")
    elif item.is_revealed and not item.is_mine and item.count > 0:
        return static(f"minesweeper/img/numeric-{item.count}.svg")
    else:
        return static("minesweeper/img/blank.svg")


@register.filter(name="alt")
def alt(item: Item) -> str:
    if item.is_flagged:
        return "Flag"
    elif item.is_revealed and item.is_mine:
        return "Mine"
    elif item.is_revealed and not item.is_mine and item.count > 0:
        return str(item.count)
    else:
        return "Blank"
