import onnxruntime as ort
from faster_whisper import WhisperModel
from kokoro import KPipeline

print("--- Dependency Check ---")
print(f"ONNX Runtime Providers: {ort.get_available_providers()}")

try:
    print("Testing faster-whisper init...")
    model = WhisperModel("tiny", device="cpu")  # tiny + cpu for quick test
    print("[SUCCESS] faster-whisper initialized")
except Exception as e:
    print(f"[FAILED] faster-whisper init: {e}")

try:
    print("Testing Kokoro init...")
    # Kokoro might try to download 80MB model
    pipeline = KPipeline(lang_code="a")
    print("[SUCCESS] Kokoro pipeline initialized")
except Exception as e:
    print(f"[FAILED] Kokoro init: {e}")
