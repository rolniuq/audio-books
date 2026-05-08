import asyncio
import edge_tts
import os
import logging
from typing import Optional, Callable
from pydub import AudioSegment
from app.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self):
        self.segment_size = settings.TTS_SEGMENT_SIZE
        self.max_retries = settings.MAX_RETRIES
        self.base_delay = settings.RETRY_BASE_DELAY
        self.max_delay = settings.RETRY_MAX_DELAY
        self.available_voices = self._get_available_voices()
    
    def _get_available_voices(self):
        return [
            {"name": "vi-VN-HoaiNeural", "language": "vi-VN", "gender": "Female"},
            {"name": "vi-VN-NamMinhNeural", "language": "vi-VN", "gender": "Male"},
            {"name": "en-US-JennyNeural", "language": "en-US", "gender": "Female"},
            {"name": "en-US-GuyNeural", "language": "en-US", "gender": "Male"},
            {"name": "ja-JP-NanamiNeural", "language": "ja-JP", "gender": "Female"},
            {"name": "zh-CN-XiaoxiaoNeural", "language": "zh-CN", "gender": "Female"},
        ]
    
    async def _synthesize_text(self, text: str, voice: str, output_file: str, rate: str = "+0%", pitch: str = "+0Hz"):
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_file)
    
    async def _synthesize_text_with_progress(self, text: str, voice: str, output_file: str, progress_callback: Optional[Callable] = None):
        communicate = edge_tts.Communicate(text, voice)
        
        with open(output_file, 'wb') as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                    if progress_callback:
                        progress_callback(len(chunk["data"]))
    
    def _get_retry_delay(self, attempt: int) -> float:
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
    
    async def _synthesize_with_retry(self, text: str, voice: str, output_file: str, rate: str = "+0%", pitch: str = "+0Hz") -> bool:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                await self._synthesize_text(text, voice, output_file, rate, pitch)
                return True
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"TTS attempt {attempt + 1} failed: {last_error}. Retrying in {delay:.1f}s...")
                    asyncio.run(asyncio.sleep(delay))
                else:
                    logger.error(f"TTS failed after {self.max_retries} attempts: {last_error}")
        
        raise Exception(f"TTS failed after {self.max_retries} retries: {last_error}")
    
    def convert_text_to_audio(
        self,
        text: str,
        output_path: str,
        voice: str = "vi-VN-HoaiNeural",
        progress_callback: Optional[Callable] = None,
        on_retry: Optional[Callable[[int, str], None]] = None
    ) -> str:
        if len(text) <= self.segment_size:
            asyncio.run(self._synthesize_with_retry(text, voice, output_path))
            return output_path
        
        segments = self._split_text_into_segments(text)
        temp_files = []
        
        for i, segment in enumerate(segments):
            temp_file = f"{output_path}.part{i}.mp3"
            try:
                asyncio.run(self._synthesize_with_retry(segment, voice, temp_file))
            except Exception as e:
                if on_retry:
                    on_retry(i + 1, str(e))
                raise
            temp_files.append(temp_file)
        
        combined = AudioSegment.from_mp3(temp_files[0])
        for temp_file in temp_files[1:]:
            combined += AudioSegment.from_mp3(temp_file)
        
        combined.export(output_path, format="mp3")
        
        for temp_file in temp_files:
            os.remove(temp_file)
        
        return output_path
    
    def _split_text_into_segments(self, text: str) -> list:
        sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
        
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            if len(current_segment) + len(sentence) <= self.segment_size:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def get_voices(self):
        return self.available_voices
    
    def get_audio_duration(self, audio_path: str) -> int:
        if not os.path.exists(audio_path):
            return 0
        
        audio = AudioSegment.from_mp3(audio_path)
        return int(audio.duration_seconds)