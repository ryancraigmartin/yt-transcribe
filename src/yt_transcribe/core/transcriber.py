"""
Audio transcription using NVIDIA NeMo Parakeet TDT.

For development/testing, this module provides a mock transcription service.
In production, it can be replaced with actual NeMo integration.

TypeScript Context:
- Similar to integrating with a speech-to-text API
- Abstract class pattern like TypeScript abstract classes/interfaces
- Factory pattern for choosing implementation (mock vs real)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import time


class TranscriptionError(Exception):
    """Raised when transcription fails."""
    pass


class TranscriptionService(ABC):
    """
    Abstract base class for transcription services.
    
    TypeScript Equivalent:
        abstract class TranscriptionService {
            abstract transcribe(audioPath: string): Promise<string>;
        }
    """
    
    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV format)
            
        Returns:
            str: Transcribed text with punctuation
            
        Raises:
            TranscriptionError: If transcription fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the transcription service is available.
        
        Returns:
            bool: True if service is ready, False otherwise
        """
        pass


class MockTranscriptionService(TranscriptionService):
    """
    Mock transcription service for testing and development.
    
    Returns a placeholder transcription based on file duration.
    This allows the application to be developed and tested without
    the heavy NeMo dependency (~2GB).
    
    TypeScript Context:
        Like a mock implementation for testing:
        class MockTranscriptionService implements TranscriptionService {
            transcribe(path: string): Promise<string> {
                return "Mock transcription..."
            }
        }
    """
    
    def transcribe(self, audio_path: Path) -> str:
        """
        Generate mock transcription.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            str: Mock transcription text
        """
        if not audio_path.exists():
            raise TranscriptionError(f"Audio file not found: {audio_path}")
        
        # Simulate some processing time (very fast compared to real transcription)
        time.sleep(0.5)
        
        # Generate mock transcription
        return f"""This is a mock transcription for {audio_path.name}.

In a production environment, this would be replaced with actual transcription 
from NVIDIA NeMo Parakeet TDT model, which provides 140x-300x real-time 
transcription speed with high accuracy and proper punctuation.

The transcription would include all spoken content from the video, properly 
formatted with punctuation, capitalization, and paragraph breaks.

To enable real transcription:
1. Install NVIDIA NeMo toolkit: pip install nemo_toolkit['all']
2. Download Parakeet TDT model (~600MB)
3. Ensure CUDA is available for GPU acceleration
4. Configure the model path in ~/.yt-transcribe/config.yaml

For development and testing purposes, this mock service allows the application 
to be fully functional without the heavy ML dependencies.
"""
    
    def is_available(self) -> bool:
        """Mock service is always available."""
        return True


class NeMoTranscriptionService(TranscriptionService):
    """
    Real transcription service using NVIDIA NeMo Parakeet TDT.
    
    This is a placeholder for the actual NeMo integration.
    When implemented, it will:
    - Load the Parakeet TDT model
    - Process audio in chunks for efficiency
    - Return transcription with proper punctuation
    
    Requirements:
    - nemo_toolkit package installed
    - CUDA-capable GPU (recommended)
    - Parakeet TDT model downloaded
    """
    
    def __init__(self, model_path: Optional[Path] = None, device: str = "cuda"):
        """
        Initialize NeMo transcription service.
        
        Args:
            model_path: Path to Parakeet model (or None to download)
            device: Device to use ('cuda' or 'cpu')
        """
        self.model_path = model_path
        self.device = device
        self._model = None
    
    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe audio using NeMo Parakeet TDT.
        
        Implementation notes:
        - Load model if not already loaded
        - Process audio file
        - Return transcription with punctuation
        """
        raise NotImplementedError(
            "NeMo transcription not yet implemented. "
            "This requires nemo_toolkit installation and model download. "
            "Use MockTranscriptionService for development."
        )
    
    def is_available(self) -> bool:
        """Check if NeMo is installed and model is available."""
        try:
            import nemo.collections.asr as nemo_asr
            return True
        except ImportError:
            return False


def get_transcription_service(use_mock: bool = True) -> TranscriptionService:
    """
    Factory function to get appropriate transcription service.
    
    Args:
        use_mock: If True, return mock service for testing
        
    Returns:
        TranscriptionService: Configured transcription service
        
    TypeScript Context:
        Factory pattern:
        const getTranscriptionService = (useMock: boolean): TranscriptionService => {
            return useMock ? new MockService() : new NeMoService()
        }
    """
    if use_mock:
        return MockTranscriptionService()
    else:
        service = NeMoTranscriptionService()
        if service.is_available():
            return service
        else:
            raise TranscriptionError(
                "NeMo transcription service not available. "
                "Install nemo_toolkit or use mock service for testing."
            )
