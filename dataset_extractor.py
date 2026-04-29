import os
import pretty_midi
def extract_guitar_midi(file_path):
    midi = pretty_midi.PrettyMIDI(file_path)
    
    filtered = []
    
    for inst in midi.instruments:
        name = pretty_midi.program_to_instrument_name(inst.program).lower()
        
        if not inst.is_drum:
            if inst.program in range(24, 32) or "guitar" in name:
                filtered.append(inst)
    
    if len(filtered) == 0:
        return None
    
    midi.instruments = filtered
    return midi

for file in os.listdir("dataset"):
    if file.endswith(".mid"):
        path = os.path.join("dataset", file)
        
        midi = extract_guitar_midi(path)
        
        if midi:
            midi.write(f"filtered/{file}")