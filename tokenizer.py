import pretty_midi
import os


def get_tempo(midi):
    """Extract tempo (BPM) from MIDI file."""
    tempo_changes = midi.get_tempo_changes()
    if len(tempo_changes[1]) > 0:
        return tempo_changes[1][0]
    return 120.0  # Default BPM


def tempo_to_token(bpm):
    """Categorize tempo into buckets."""
    if bpm < 60:
        return "TEMPO_VERY_SLOW"
    elif bpm < 90:
        return "TEMPO_SLOW"
    elif bpm < 120:
        return "TEMPO_MEDIUM"
    elif bpm < 150:
        return "TEMPO_FAST"
    else:
        return "TEMPO_VERY_FAST"


def midi_to_tokens(midi_path):
    """Convert MIDI file to token sequence."""
    midi = pretty_midi.PrettyMIDI(midi_path)
    
    # Get tempo
    bpm = get_tempo(midi)
    tempo_token = tempo_to_token(bpm)
    
    tokens = []
    tokens.append(f"TEMPO:{tempo_token}:{bpm}")
    
    # Collect all notes from all instruments
    all_notes = []
    for inst in midi.instruments:
        if not inst.is_drum:
            for note in inst.notes:
                all_notes.append(note)
    
    # Sort by start time
    all_notes.sort(key=lambda x: x.start)
    
    # Convert to tokens
    prev_time = 0
    for note in all_notes:
        # Time delta (in beats, assuming 4/4 time)
        delta = note.start - prev_time
        tokens.append(f"TIME:{delta:.3f}")
        
        # Note: pitch, duration, velocity
        tokens.append(f"NOTE:{note.pitch}:{note.duration:.3f}:{note.velocity}")
        
        prev_time = note.start
    
    return tokens


def process_folder(input_dir, output_file):
    """Process all MIDI files in a folder."""
    all_tokens = []
    
    for file in os.listdir(input_dir):
        if file.endswith(".mid"):
            path = os.path.join(input_dir, file)
            print(f"Processing: {file}")
            
            try:
                tokens = midi_to_tokens(path)
                all_tokens.append(f"FILE:{file}")
                all_tokens.extend(tokens)
                all_tokens.append("")  # Blank line between files
            except Exception as e:
                print(f"Error processing {file}: {e}")
    
    # Write to output
    with open(output_file, "w") as f:
        f.write("\n".join(all_tokens))
    
    print(f"\nTokenized {len(all_tokens)} tokens to {output_file}")


if __name__ == "__main__":
    process_folder("filtered", "tokens.txt")