import pretty_midi
import os


def get_tempo(midi):
    """Extract tempo (BPM) from MIDI file."""
    tempo_changes = midi.get_tempo_changes()
    if len(tempo_changes[1]) > 0:
        return tempo_changes[1][0]
    return 120.0


def midi_to_sm_format(midi_path):
    """Convert MIDI to SM format: pitch start_time end_time velocity"""
    midi = pretty_midi.PrettyMIDI(midi_path)
    
    bpm = get_tempo(midi)
    notes_data = []
    
    # Include tempo as comment
    notes_data.append(f"# TEMPO: {bpm}")
    
    # Collect all notes from non-drum instruments
    all_notes = []
    for inst in midi.instruments:
        if not inst.is_drum:
            for note in inst.notes:
                all_notes.append(note)
    
    # Sort by start time
    all_notes.sort(key=lambda x: x.start)
    
    # Convert to SM format: pitch start_time end_time velocity
    for note in all_notes:
        start = note.start
        end = note.start + note.duration
        line = f"{note.pitch} {start:.3f} {end:.3f} {note.velocity}"
        notes_data.append(line)
    
    return notes_data


def process_folder(input_dir, output_file):
    """Process all MIDI files in a folder."""
    all_lines = []
    
    for file in os.listdir(input_dir):
        if file.endswith(".mid"):
            path = os.path.join(input_dir, file)
            print(f"Processing: {file}")
            
            try:
                lines = midi_to_sm_format(path)
                all_lines.append(f"# FILE: {file}")
                all_lines.extend(lines)
                all_lines.append("")  # Blank line between files
            except Exception as e:
                print(f"Error processing {file}: {e}")
    
    # Write to output
    with open(output_file, "w") as f:
        f.write("\n".join(all_lines))
    
    print(f"\nProcessed {len([l for l in all_lines if l and not l.startswith('#')])} notes to {output_file}")


if __name__ == "__main__":
    process_folder("filtered", "sm_notes.txt")