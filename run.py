import os
import json
import argparse
from src.agent import ZentroMartAgent
from src.voice import voice_turn, synthesize_response

def run_batch(input_dir: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    agent = ZentroMartAgent()
    logs = []
    
    audio_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".wav")])
    print(f"Total audio files found: {len(audio_files)}")

    for fname in audio_files:
        in_path = os.path.join(input_dir, fname)
        out_audio_name = f"reply_{fname}"
        out_audio_path = os.path.join(output_dir, out_audio_name)
        
        print(f"Processing {fname}...")
        heard, reply, sources = voice_turn(in_path, agent)
        synthesize_response(reply, out_audio_path)
        
        logs.append({
            "input_file": fname,
            "transcription": heard,
            "reply_text": reply,
            "output_audio": out_audio_name,
            "retrieved_sources": sources
        })
        
    with open(os.path.join(output_dir, "batch_results.json"), "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)
    print("Done! Results saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    args = parser.parse_args()
    run_batch(args.input_dir, args.output_dir)