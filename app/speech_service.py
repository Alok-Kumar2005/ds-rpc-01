import assemblyai as aai
import tempfile
import os

class AudioTranscriber:
    def __init__(self, api_key):
        aai.settings.api_key = api_key
        self.config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            language_detection=True,
            punctuate=True,
            format_text=True
        )
        self.transcriber = aai.Transcriber(config=self.config)
    
    def transcribe_bytes(self, audio_bytes):
        """Transcribe audio bytes to text"""
        try:
            if not audio_bytes or len(audio_bytes) == 0:
                return {"success": False, "error": "No audio data provided"}
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Check file size
            file_size = os.path.getsize(tmp_file_path)
            if file_size < 1000:  # Less than 1KB might be too small
                os.unlink(tmp_file_path)
                return {"success": False, "error": f"Audio file too small ({file_size} bytes). Please record a longer message."}
            
            # Transcribe
            transcript = self.transcriber.transcribe(tmp_file_path)
            
            # Cleanup
            try:
                os.unlink(tmp_file_path)
            except:
                pass
            
            # Check result
            if transcript.status == aai.TranscriptStatus.error:
                return {"success": False, "error": f"Transcription failed: {transcript.error}"}
            elif transcript.status == aai.TranscriptStatus.completed:
                if transcript.text and len(transcript.text.strip()) > 0:
                    return {"success": True, "text": transcript.text.strip()}
                else:
                    return {"success": False, "error": "No speech detected. Please speak clearly and try again."}
            else:
                return {"success": False, "error": f"Unexpected status: {transcript.status}"}
                
        except Exception as e:
            return {"success": False, "error": f"Transcription error: {str(e)}"}

# Usage example:
# transcriber = AudioTranscriber("your_api_key_here")
# result = transcriber.transcribe_bytes(audio_bytes)
# if result["success"]:
#     print(result["text"])
# else:
#     print(result["error"]) 