from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .channels import Channel
    from .internals import CacheHandler
    from .types import CategoryPayload


class Category:
    """
    A class that represents a Voltage category.

    Attributes
    ----------
    id: :class:`str`
        The category's ID.
    name: :class:`str`
        The name of the category.
    description: Optional[:class:`str`]
        The name of the category.
    channels: List[:class:`Channel`]
        A list of all channels in the category.
    """

    __slots__ = ("name", "id", "channel_ids", "cache", "description")

    def __init__(self, data: CategoryPayload, cache: CacheHandler):
        self.name = data["title"]
        self.description = data.get("description")
        self.id = data["id"]
        self.channel_ids = data["channels"]
        self.cache = cache

    @property
    def channels(self) -> list[Channel]:
        return [self.cache.get_channel(id) for id in self.channel_ids]

    def __repr__(self):
        return f"<Category {self.name}>"

    def __str__(self):
        return self.name
