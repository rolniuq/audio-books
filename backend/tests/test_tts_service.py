import pytest
import asyncio
import tempfile
import os
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.tts_service import TTSService
from app.config import settings


class TestTTSService:
    @pytest.fixture
    def tts_service(self):
        return TTSService()
    
    def test_tts_service_init(self, tts_service):
        assert tts_service is not None
        assert tts_service.segment_size == settings.TTS_SEGMENT_SIZE
        assert tts_service.max_retries == settings.MAX_RETRIES
    
    def test_get_available_voices(self, tts_service):
        voices = tts_service.get_voices()
        assert isinstance(voices, list)
        assert len(voices) > 0
        assert any(v["name"] == "vi-VN-HoaiMyNeural" for v in voices)
    
    def test_get_retry_delay_exponential(self, tts_service):
        delay_0 = tts_service._get_retry_delay(0)
        delay_1 = tts_service._get_retry_delay(1)
        delay_2 = tts_service._get_retry_delay(2)
        
        assert delay_0 < delay_1 < delay_2
    
    def test_get_retry_delay_capped(self, tts_service):
        for attempt in range(10):
            delay = tts_service._get_retry_delay(attempt)
            assert delay <= settings.RETRY_MAX_DELAY
    
    @pytest.mark.asyncio
    async def test_synthesize_with_retry_success(self, tts_service):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = f.name
        
        try:
            with patch('edge_tts.Communicate') as mock_communicate:
                mock_instance = AsyncMock()
                mock_instance.save = AsyncMock()
                mock_communicate.return_value = mock_instance
                
                result = await tts_service._synthesize_with_retry(
                    "Test text", "vi-VN-HoaiMyNeural", output_path
                )
                assert result is True
                mock_instance.save.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    @pytest.mark.asyncio
    async def test_synthesize_with_retry_eventual_failure(self, tts_service):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = f.name
        
        try:
            with patch('edge_tts.Communicate') as mock_communicate:
                mock_instance = AsyncMock()
                mock_instance.save = AsyncMock(side_effect=Exception("Network error"))
                mock_communicate.return_value = mock_instance
                
                with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                    with pytest.raises(Exception) as exc_info:
                        await tts_service._synthesize_with_retry(
                            "Test text", "vi-VN-HoaiMyNeural", output_path
                        )
                    
                    assert "failed after" in str(exc_info.value)
                    assert mock_instance.save.call_count == settings.MAX_RETRIES
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    @pytest.mark.asyncio
    async def test_synthesize_with_retry_success_after_one_failure(self, tts_service):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = f.name
        
        try:
            with patch('edge_tts.Communicate') as mock_communicate:
                mock_instance = AsyncMock()
                mock_instance.save = AsyncMock(side_effect=[
                    Exception("Temporary error"),
                    None
                ])
                mock_communicate.return_value = mock_instance
                
                with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                    result = await tts_service._synthesize_with_retry(
                        "Test text", "vi-VN-HoaiMyNeural", output_path
                    )
                    assert result is True
                    assert mock_instance.save.call_count == 2
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_convert_text_to_audio_short_text(self, tts_service):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = f.name
        
        try:
            with patch.object(tts_service, '_synthesize_with_retry', new_callable=AsyncMock) as mock_synth:
                mock_synth.return_value = True
                result = tts_service.convert_text_to_audio(
                    "Short text", output_path, "vi-VN-HoaiMyNeural"
                )
                assert result == output_path
                mock_synth.assert_called_once()
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_convert_text_to_audio_with_retry_callback(self, tts_service):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            output_path = f.name
        
        retry_calls = []
        def on_retry(attempt, error):
            retry_calls.append((attempt, error))
        
        try:
            with patch.object(tts_service, '_synthesize_with_retry', new_callable=AsyncMock) as mock_synth:
                mock_synth.return_value = True
                tts_service.convert_text_to_audio(
                    "Short text", output_path, "vi-VN-HoaiMyNeural", on_retry=on_retry
                )
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_get_audio_duration_nonexistent_file(self, tts_service):
        duration = tts_service.get_audio_duration("/nonexistent/file.mp3")
        assert duration == 0
    
    def test_split_text_into_segments(self, tts_service):
        tts_service.segment_size = 100
        text = "This is sentence one. " * 10
        segments = tts_service._split_text_into_segments(text)
        
        assert isinstance(segments, list)
        assert len(segments) > 0
        for segment in segments:
            assert len(segment) <= tts_service.segment_size + 50
    
    def test_split_text_preserves_sentence_boundaries(self, tts_service):
        tts_service.segment_size = 50
        text = "Short sentence. Another sentence here. Third one."
        segments = tts_service._split_text_into_segments(text)
        
        assert all("." in seg or seg == segments[-1] for seg in segments if len(segments) == 1 or seg != segments[-1])