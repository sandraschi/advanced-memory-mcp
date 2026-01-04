import os
from pathlib import Path

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel
from kokoro import KPipeline

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

print("\n--- Audio Soul 2026 Verification ---", flush=True)

# 1. Test faster-whisper on GPU
try:
    print("\n[1/2] Initializing faster-whisper (tiny) on GPU...", flush=True)
    model = WhisperModel("tiny", device="cuda", compute_type="float16")
    print("[SUCCESS] faster-whisper loaded on CUDA.", flush=True)
except Exception as e:
    print(f"[FAILED] faster-whisper: {e}", flush=True)

# 2. Test Kokoro Synthesis
try:
    print("\n[2/2] Initializing Kokoro Pipeline...", flush=True)
    pipeline = KPipeline(lang_code="a")
    print("[SUCCESS] Kokoro pipeline initialized.", flush=True)

    test_text = "The audio stack upgrade is complete. Sandra's voice is now soulful and efficient. Materialism rules."
    print(f"Synthesizing: '{test_text}'", flush=True)

    generator = pipeline(test_text, voice="af_heart", speed=1.0)
    audio_segments = []
    for gs, ps, audio in generator:
        audio_segments.append(audio)

    full_audio = np.concatenate(audio_segments)

    output_dir = Path("tests/output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "audio_soul_test.wav"

    sf.write(str(output_file), full_audio, 24000)
    print(f"[SUCCESS] Audio saved to {output_file}", flush=True)
    print(f"Audio duration: {len(full_audio) / 24000:.2f} seconds", flush=True)

except Exception as e:
    print(f"[FAILED] Kokoro: {e}", flush=True)
    import traceback

    traceback.print_exc()

print("\n--- Verification Complete ---", flush=True)
