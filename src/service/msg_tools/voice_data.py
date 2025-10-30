import asyncio
import io
from html import escape
from typing import List, Optional

import speech_recognition as sr
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from src.service.loggers.py_logger_tel_bot import get_logger

logger = get_logger(__name__)


class VoiceMessageAsync:
    def __init__(self, message: Message):
        self.message = message

    async def _download_ogg_bytes(self) -> bytes:
        """Async завантаження голосового як байтів без збереження на диск."""
        if not self.message or not getattr(self.message, "voice", None):
            msg = "No voice message to download."
            logger.error(msg)
            raise ValueError(msg)
        bot = self.message.bot
        voice = self.message.voice
        # 1) отримуємо File по file_id
        file = await bot.get_file(voice.file_id)
        # 2) завантажуємо у пам'ять
        buf = io.BytesIO()
        await bot.download_file(file.file_path, destination=buf)
        return buf.getvalue()

    async def _ogg_to_wav_bytes(self, ogg_bytes: bytes, wav_path: Optional[str] = None) -> bytes:
        """
        OGG(Opus) -> WAV (PCM 16-bit mono 16k) через ffmpeg.
        Якщо задано wav_path — пише одразу на диск у WAV (без .ogg).
        """
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-i",
            "pipe:0",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            "pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(input=ogg_bytes), timeout=60)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            raise RuntimeError("ffmpeg conversion timeout")

        if proc.returncode != 0:
            logger.error("ffmpeg failed: %s", stderr.decode("utf-8", errors="ignore"))
            raise RuntimeError("ffmpeg conversion failed")

        if wav_path:
            with open(wav_path, "wb") as f:
                f.write(stdout)

        return stdout

    async def _recognize_google_wav_bytes(self, wav_bytes: bytes, languages: List[str]) -> str:
        """
        SpeechRecognition є блокуючою — запускаємо у треді.
        Пробуємо мови по черзі; повертаємо перший успішний текст.
        """

        def _run(lang: str) -> Optional[str]:
            recognizer = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
                audio = recognizer.record(source)
            try:
                return recognizer.recognize_google(audio, language=lang)
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                # проблеми мережі/квот — логнемо і спробуємо іншу мову
                logger.warning(f"Google STT RequestError for {lang}: {e}")
                return None

        for lang in languages:
            text = await asyncio.wait_for(asyncio.to_thread(_run, lang), timeout=30)
            if text:
                return text
        raise sr.UnknownValueError("Не вдалося розпізнати мовами: " + ", ".join(languages))

    async def voice_to_text(
        self,
        save_wav_path: Optional[str] = None,
        languages: Optional[List[str]] = None,
    ) -> str:
        """
        1) завантаження OGG у пам'ять
        2) ffmpeg -> WAV (опціонально збереження на диск)
        3) розпізнавання (у треді)
        """
        if languages is None:
            languages = ["uk-UA", "ru-RU", "en-US"]

        ogg_bytes = await self._download_ogg_bytes()
        wav_bytes = await self._ogg_to_wav_bytes(ogg_bytes, wav_path=save_wav_path)
        text = await self._recognize_google_wav_bytes(wav_bytes, languages)
        return text.strip()

    async def safe_reply(self, text: str, html: bool = False) -> None:
        try:
            if html:
                await self.message.reply(text, parse_mode="HTML")
            else:
                await self.message.reply(text)
        except TelegramAPIError as e:
            logger.error(f"Telegram API error on reply: {e}")
        except Exception as e:
            logger.error(f"Unexpected error on reply: {e}")


async def handle_voice(message: Message) -> None:
    """Обробка голосового повідомлення."""
    vm = VoiceMessageAsync(message)
    try:
        raw_text = await vm.voice_to_text()
        if not raw_text:
            return await vm.safe_reply("Не вдалося розпізнати мовлення 🤷")

        logger.info(
            f"Voice message from {getattr(message.from_user, 'id', 'unknown')}" f" recognized as: {raw_text[:50]}"
        )
        safe_html = escape(raw_text)
        header_single = "<u>стенограма</u>:\n"
        header_part_tpl = "<u>стенограма (частина {n})</u>:\n"
        limit = 4000  # запас до 4096

        # Якщо вміщується як одне повідомлення
        if len(header_single) + len(safe_html) <= limit:
            await vm.safe_reply(f"{header_single}{safe_html}", html=True)
        else:
            i, n = 0, 1
            while i < len(safe_html):
                header_part = header_part_tpl.format(n=n)
                room = limit - len(header_part)
                chunk = safe_html[i : i + room]
                await vm.safe_reply(f"{header_part}{chunk}", html=True)
                i += room
                n += 1
    except sr.UnknownValueError:
        text = "Не вдалося розпізнати мову/мовлення у голосовому повідомленні 🤷"
        await vm.safe_reply(text)
    except Exception as e:
        logger.error(f"Voice handling failed: {e}")
        text = f"Сталася помилка обробки голосового повідомлення:\n{e}"
        await vm.safe_reply(text)
