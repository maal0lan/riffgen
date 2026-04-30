import pretty_midi
import json



def analyze_midi(file_path):
    midi = pretty_midi.PrettyMIDI(file_path)
    
    instruments = []
    
    for inst in midi.instruments:
        instruments.append({
            "program": int(inst.program),
            "name": pretty_midi.program_to_instrument_name(inst.program),
            "is_drum": bool(inst.is_drum),
            "num_notes": int(len(inst.notes))
        })
    
    return {
        "file": file_path,
        "num_instruments": int(len(midi.instruments)),
        "instruments": instruments
    }

data = analyze_midi("filtered/Andra_tutto_bene_58_.mid")

with open("midi_analysis.json", "w") as f:
    json.dump(data, f, indent=4)