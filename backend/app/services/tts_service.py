import asyncio
import edge_tts
import os
import logging
from typing import Optional, Callable
from pydub import AudioSegment
from app.config import settings

logger = logging.getLogger(__name__)

TTS_TIMEOUT = 600  # 10 minutes max per segment


class TTSService:
    def __init__(self):
        self.segment_size = settings.TTS_SEGMENT_SIZE
        self.max_retries = settings.MAX_RETRIES
        self.base_delay = settings.RETRY_BASE_DELAY
        self.max_delay = settings.RETRY_MAX_DELAY
        self.available_voices = self._get_available_voices()
    
    def _get_available_voices(self):
        return [
            {"name": "vi-VN-HoaiMyNeural", "language": "vi-VN", "gender": "Female"},
            {"name": "vi-VN-NamMinhNeural", "language": "vi-VN", "gender": "Male"},
            {"name": "en-US-JennyNeural", "language": "en-US", "gender": "Female"},
            {"name": "en-US-GuyNeural", "language": "en-US", "gender": "Male"},
            {"name": "en-GB-SoniaNeural", "language": "en-GB", "gender": "Female"},
            {"name": "ja-JP-NanamiNeural", "language": "ja-JP", "gender": "Female"},
            {"name": "zh-CN-XiaoxiaoNeural", "language": "zh-CN", "gender": "Female"},
        ]
    
    def _get_vietnamese_ratio(self, text: str) -> float:
        if not text or len(text) == 0:
            return 0.0
        import re
        vietnamese_chars = 'àáảãạăằắẳẵặâầấẩẫặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộùúủũụừứửữựỳýỷỹỵđ'
        vietnamese_pattern = re.compile(f'[{vietnamese_chars}]', re.IGNORECASE)
        vi_count = len(vietnamese_pattern.findall(text))
        return vi_count / len(text)

    def _get_corrupted_vietnamese_ratio(self, text: str) -> float:
        """Detect Vietnamese text that has been corrupted with middle dots (U+00B7)"""
        if not text or len(text) == 0:
            return 0.0
            
        # Pattern for corrupted Vietnamese: sequences like [a-z]·[a-z] where · replaces diacritics
        import re
        # Look for patterns where a letter is followed by a middle dot and another letter
        # This is characteristic of corrupted Vietnamese text where diacritics became middle dots
        corrupted_pattern = re.compile(r'[a-zA-Z]·[a-zA-Z]')
        corrupted_matches = len(corrupted_pattern.findall(text))
        
        # Also count actual Vietnamese characters
        vietnamese_chars = 'àáảãạăằắẳẵặâầấẩẫặèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộùúủũụừứửữựỳýỷỹỵđ'
        vietnamese_pattern = re.compile(f'[{vietnamese_chars}]', re.IGNORECASE)
        vi_count = len(vietnamese_pattern.findall(text))
        
        # Combine both signals
        total_score = (vi_count * 2) + corrupted_matches  # Weight actual Vietnamese chars higher
        return total_score / (len(text) * 2) if len(text) > 0 else 0.0

    def _detect_language(self, text: str) -> str:
        if not text or len(text) == 0:
            return "en-US"
        
        import re
        vietnamese_chars = 'àáảãạăằắẳẵặâầấẩẫặèéẻẹêềếểễệìíỉĩịòóõọôồốổỗộùúủũụừứửữựỳýỷỹỵđ'
        vietnamese_pattern = re.compile(f'[{vietnamese_chars}]', re.IGNORECASE)
        vi_count = len(vietnamese_pattern.findall(text))
        total_chars = len(text)
        
        # Log detection info for debugging
        logger.debug(f"Vietnamese char count: {vi_count}/{total_chars} = {vi_count/total_chars if total_chars > 0 else 0}")
        
        # Also check for corrupted Vietnamese text (where diacritics became middle dots)
        corrupted_ratio = self._get_corrupted_vietnamese_ratio(text)
        logger.debug(f"Corrupted Vietnamese ratio: {corrupted_ratio}")
        
        # Combined detection: either actual Vietnamese chars OR corrupted pattern
        direct_ratio = vi_count / total_chars if total_chars > 0 else 0
        combined_ratio = max(direct_ratio, corrupted_ratio)
        
        # Lower threshold for better detection of Vietnamese text
        if total_chars > 0 and combined_ratio > 0.05:  # Even lower threshold to catch corrupted text
            return "vi-VN"
        return "en-US"
    
    def _get_voice_for_text(self, text: str, preferred_voice: str = None) -> str:
        if preferred_voice:
            voice_lang = next((v["language"] for v in self.available_voices if v["name"] == preferred_voice), None)
            if voice_lang:
                text_lang = self._detect_language(text)
                if voice_lang == text_lang:
                    return preferred_voice
        
        text_lang = self._detect_language(text)
        for voice in self.available_voices:
            if voice["language"] == text_lang:
                return voice["name"]
        
        return preferred_voice or self.available_voices[0]["name"]
    
    async def _synthesize_text(self, text: str, voice: str, output_file: str, rate: str = "+0%", pitch: str = "+0Hz"):
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await asyncio.wait_for(communicate.save(output_file), timeout=TTS_TIMEOUT)
    
    async def _synthesize_text_with_progress(self, text: str, voice: str, output_file: str, progress_callback: Optional[Callable] = None):
        communicate = edge_tts.Communicate(text, voice)
        
        async def stream_with_timeout():
            with open(output_file, 'wb') as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                        if progress_callback:
                            progress_callback(len(chunk["data"]))
        
        await asyncio.wait_for(stream_with_timeout(), timeout=TTS_TIMEOUT)
    
    def _get_retry_delay(self, attempt: int) -> float:
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
    
    async def _synthesize_with_retry(self, text: str, voice: str, output_file: str, rate: str = "+0%", pitch: str = "+0Hz") -> bool:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                await self._synthesize_text(text, voice, output_file, rate, pitch)
                return True
            except asyncio.TimeoutError as e:
                last_error = "TTS timeout"
                logger.error(f"TTS timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"TTS attempt {attempt + 1} timed out. Retrying in {delay:.1f}s (text len={len(text)})...")
                    await asyncio.sleep(delay)
                else:
                    raise  # Let outer timeout handle it
            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.warning(f"TTS attempt {attempt + 1} failed: {last_error}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"TTS failed after {self.max_retries} attempts: {last_error}")
        
        raise Exception(f"TTS failed after {self.max_retries} retries: {last_error}")
    
    async def _convert_text_to_audio_async(
        self,
        text: str,
        output_path: str,
        voice: str = "vi-VN-HoaiMyNeural",
        progress_callback: Optional[Callable] = None,
        on_retry: Optional[Callable[[int, str], None]] = None
    ) -> str:
        voice = self._get_voice_for_text(text, voice)
        if len(text) <= self.segment_size:
            await self._synthesize_with_retry(text, voice, output_path)
            return output_path
        
        segments = self._split_text_into_segments(text)
        temp_files = []
        
        for i, segment in enumerate(segments):
            temp_file = f"{output_path}.part{i}.mp3"
            try:
                await self._synthesize_with_retry(segment, voice, temp_file)
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
    
    def convert_text_to_audio(
        self,
        text: str,
        output_path: str,
        voice: str = "vi-VN-HoaiMyNeural",
        progress_callback: Optional[Callable] = None,
        on_retry: Optional[Callable[[int, str], None]] = None
    ) -> str:
        return asyncio.run(self._convert_text_to_audio_async(text, output_path, voice, progress_callback, on_retry))
    
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