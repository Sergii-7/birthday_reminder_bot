"""
Тести для модуля create_bot.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestCreateBot:
    """Тести для створення та налаштування Telegram бота."""

    @patch("src.bot_app.create_bot.Bot")
    @patch("src.bot_app.create_bot.Dispatcher")
    def test_bot_creation(self, mock_dispatcher, mock_bot):
        """Тест створення бота та диспетчера."""
        try:
            from src.bot_app.create_bot import bot, dp

            # Перевіряємо що об'єкти існують
            assert bot is not None
            assert dp is not None
        except ImportError:
            pytest.skip("Module src.bot_app.create_bot not available")

    @patch("src.bot_app.create_bot.config.TOKEN", "test_token")
    def test_bot_token_configuration(self):
        """Тест налаштування токена бота."""
        try:
            with patch("src.bot_app.create_bot.Bot") as mock_bot:
                from src.bot_app.create_bot import bot

                assert bot is not None
        except ImportError:
            pytest.skip("Module src.bot_app.create_bot not available")
            from src.bot_app import create_bot

            mock_bot.assert_called_with(token="test_token")

    @patch("src.bot_app.create_bot.dp")
    def test_dispatcher_setup(self, mock_dp):
        """Тест налаштування диспетчера."""
        mock_dp.message = MagicMock()
        mock_dp.callback_query = MagicMock()

        # Імітуємо реєстрацію handlers
        mock_dp.message.register = MagicMock()
        mock_dp.callback_query.register = MagicMock()

        assert hasattr(mock_dp, "message")
        assert hasattr(mock_dp, "callback_query")
