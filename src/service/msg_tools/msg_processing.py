from typing import Optional

from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


class ToolsProcessing:
    """Class for processing messages."""

    @staticmethod
    async def process_voice_message(voice_data: bytes) -> Optional[str]:
        """Process voice message and return text."""
        try:
            # Simulate processing voice data (e.g., speech-to-text)
            processed_text = "Processed voice message text"
            return processed_text
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            return None

    @staticmethod
    async def process_text_message(text: str) -> Optional[str]: ...


async def _demo():
    """Demo function for MsgProcessing."""
    msg = " Hello, World! "
    processed = ToolsProcessing()
    text_processed_msg = processed.process_text_message(msg)
    print(f"Original: '{msg}' | Processed: '{text_processed_msg}'")


if __name__ == "__main__":
    """Test module."""
    import asyncio

    asyncio.run(_demo())
