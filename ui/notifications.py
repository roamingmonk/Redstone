
"""Utility helpers for rendering short-lived floating notifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

import pygame

DEFAULT_COLOR = (255, 223, 0)  # Warm gold similar to XP highlight
DEFAULT_FONT_KEY = "normal"
DEFAULT_DURATION = 2200  # milliseconds
DEFAULT_RISE_DISTANCE = 60
STACK_SPACING = 32


@dataclass
class FloatingTextMessage:
    """Represents a single floating text instance."""

    text: str
    color: Tuple[int, int, int]
    start_time: int
    duration: int
    position: Tuple[int, int]
    font_key: str
    rise_distance: int
    shadow: bool = True

    def is_active(self, current_time: int) -> bool:
        return current_time - self.start_time < self.duration


class FloatingTextManager:
    """Maintain and render floating text notifications across screens."""

    def __init__(self):
        self._messages: List[FloatingTextMessage] = []
        self.default_position: Tuple[int, int] = (512, 730)  # position of text at start  org (512, 140)

    # ------------------------------------------------------------------
    # Message management helpers
    # ------------------------------------------------------------------
    def add_message(
        self,
        text: str,
        *,
        color: Tuple[int, int, int] = DEFAULT_COLOR,
        duration: int = DEFAULT_DURATION,
        position: Optional[Tuple[int, int]] = None,
        font_key: str = DEFAULT_FONT_KEY,
        rise_distance: int = DEFAULT_RISE_DISTANCE,
        shadow: bool = True,
    ) -> None:
        if not text:
            return

        start_pos = position if position is not None else self.default_position
        message = FloatingTextMessage(
            text=text,
            color=color,
            start_time=pygame.time.get_ticks(),
            duration=max(500, duration),  # prevent super short flashes
            position=start_pos,
            font_key=font_key or DEFAULT_FONT_KEY,
            rise_distance=rise_distance,
            shadow=shadow,
        )
        self._messages.append(message)

    def handle_show_event(self, event_data: Optional[Dict] = None) -> None:
        data = event_data or {}
        text = data.get("text")
        amount = data.get("amount")

        if not text and amount is not None:
            text = f"+{amount} XP"
            reason = data.get("reason")
            if reason:
                text = f"{text} - {reason}"

        raw_color = data.get("color", DEFAULT_COLOR)
        if isinstance(raw_color, (list, tuple)) and len(raw_color) >= 3:
            color = tuple(int(c) for c in raw_color[:3])
        else:
            color = DEFAULT_COLOR
        duration = int(data.get("duration", DEFAULT_DURATION))
        raw_position = data.get("position")
        position: Optional[Tuple[int, int]]
        if isinstance(raw_position, (list, tuple)) and len(raw_position) >= 2:
            position = (int(raw_position[0]), int(raw_position[1]))
        else:
            position = None
        font_key = data.get("font", DEFAULT_FONT_KEY)
        rise_distance = int(data.get("rise_distance", DEFAULT_RISE_DISTANCE))
        shadow = bool(data.get("shadow", True))

        self.add_message(
            text,
            color=color,
            duration=duration,
            position=position,
            font_key=font_key,
            rise_distance=rise_distance,
            shadow=shadow,
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, fonts: Optional[Dict]) -> None:
        if not self._messages:
            return

        current_time = pygame.time.get_ticks()
        active_messages: List[FloatingTextMessage] = []

        for message in sorted(self._messages, key=lambda msg: msg.start_time):
            if not message.is_active(current_time):
                continue

            progress = (current_time - message.start_time) / message.duration
            alpha = max(0, min(255, int(255 * (1 - progress))))

            x, y = message.position
            y_offset = message.rise_distance * progress
            draw_y = y - y_offset - (len(active_messages) * STACK_SPACING)

            font = None
            if fonts:
                font = fonts.get(message.font_key) or fonts.get(DEFAULT_FONT_KEY)
            if font is None:
                font = pygame.font.Font(None, 28)

            text_surface = font.render(message.text, True, message.color)
            text_surface = text_surface.convert_alpha()
            text_surface.set_alpha(alpha)

            text_rect = text_surface.get_rect(center=(x, int(draw_y)))

            if message.shadow:
                shadow_surface = font.render(message.text, True, (0, 0, 0))
                shadow_surface = shadow_surface.convert_alpha()
                shadow_surface.set_alpha(int(alpha * 0.6))
                shadow_rect = shadow_surface.get_rect(center=(x + 2, int(draw_y) + 2))
                surface.blit(shadow_surface, shadow_rect)

            surface.blit(text_surface, text_rect)
            active_messages.append(message)

        self._messages = active_messages

    def clear(self) -> None:
        self._messages.clear()
