from mido import Message, MidiFile, MidiTrack

def tokens_to_midi(tokens, output_file="output.mid"):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # 🎸 Set instrument to guitar
    track.append(Message('program_change', program=24, time=0))
    # 24 = Nylon Guitar (General MIDI)

    current_notes = []
    velocity = 80
    duration = 120

    for token in tokens:
        if token.startswith("NOTE_"):
            note = int(token.split("_")[1])
            current_notes.append(note)

        elif token.startswith("VEL_"):
            if "HIGH" in token:
                velocity = 100
            elif "MID" in token:
                velocity = 80
            else:
                velocity = 60

        elif token.startswith("DUR_"):
            duration = int(token.split("_")[1]) * 120

        elif token == "CHORD_END":
            for note in current_notes:
                track.append(Message('note_on', note=note, velocity=velocity, time=0))

            for note in current_notes:
                track.append(Message('note_off', note=note, velocity=velocity, time=duration))

            current_notes = []

    mid.save(output_file)
    print(f"Saved MIDI: {output_file}")# Example usage
if __name__ == "__main__":
    # Load tokens from file
    with open("generated_outputs/notes.txt", "r") as f:
        tokens = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(tokens)} tokens")
    tokens_to_midi(tokens, "generated_outputs/generated_riff_01.mid")
    print("Done!")