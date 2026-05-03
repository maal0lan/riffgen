import mido
from mido import Message, MidiFile, MidiTrack
import os
from collections import defaultdict


def get_tempo(midi_file):
    """Extract tempo from MIDI file."""
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                return mido.tempo2bpm(msg.tempo)
    return 120.0


def tempo_to_token(bpm):
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


def velocity_to_token(v):
    if v < 60:
        return "VEL_LOW"
    elif v < 100:
        return "VEL_MID"
    else:
        return "VEL_HIGH"


def midi_to_tokens(midi_path):
    midi = mido.MidiFile(midi_path)

    tokens = []

    # ✅ tempo
    bpm = get_tempo(midi)
    tokens.append(tempo_to_token(bpm))

    # ✅ collect notes with instrument tag
    all_notes = []

    # Track note_on events to calculate duration
    note_on_times = {}
    note_velocities = {}

    for track in midi.tracks:
        current_time = 0
        track_name = None
        
        # First pass: get track name
        for msg in track:
            if msg.type == 'track_name':
                track_name = msg.name
                break
        
        # Second pass: process notes
        for msg in track:
            current_time += msg.time

            if msg.type == 'note_on' and msg.velocity > 0:
                # Store note start time and velocity
                note_on_times[msg.note] = current_time
                note_velocities[msg.note] = msg.velocity

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                # Note ended - calculate duration
                if msg.note in note_on_times:
                    start_time = note_on_times[msg.note]
                    velocity = note_velocities[msg.note]
                    duration = current_time - start_time

                    # Use track name if available, otherwise use "ALL"
                    if track_name:
                        inst_type = track_name[:20]  # Limit length for token
                    else:
                        inst_type = "ALL"

                    all_notes.append((start_time, msg.note, duration, velocity, inst_type))

                    del note_on_times[msg.note]
                    del note_velocities[msg.note]

    # ✅ sort by time
    all_notes.sort(key=lambda x: x[0])

    # ✅ group by time (for chords)
    grouped = defaultdict(list)
    for start_time, pitch, duration, velocity, inst_type in all_notes:
        t = round(start_time, 3)
        grouped[t].append((pitch, duration, velocity, inst_type))

    prev_time = 0

    # ✅ build tokens
    for t in sorted(grouped.keys()):
        delta = t - prev_time

        # ⏱ discretize time
        if delta > 0:
            time_bin = int(delta * 10)
            tokens.append(f"TIME_{time_bin}")

        tokens.append("CHORD_START")

        for pitch, duration, velocity, inst_type in grouped[t]:
            dur_bin = int(duration * 10)
            vel_token = velocity_to_token(velocity)

            tokens.append(f"INST_{inst_type}")
            tokens.append(f"NOTE_{pitch}")
            tokens.append(f"DUR_{dur_bin}")
            tokens.append(vel_token)

        tokens.append("CHORD_END")

        prev_time = t

    return tokens


def process_folder(input_dir, output_file):
    all_tokens = []

    for file in os.listdir(input_dir):
        if file.endswith(".mid"):
            path = os.path.join(input_dir, file)
            print(f"Processing: {file}")

            try:
                tokens = midi_to_tokens(path)
                all_tokens.append(f"FILE_{file}")
                all_tokens.extend(tokens)
                all_tokens.append("")
            except Exception as e:
                print(f"Error processing {file}: {e}")

    with open(output_file, "w") as f:
        f.write("\n".join(all_tokens))

    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    #process_folder("filtered", "output_tokenizer/tokens_clean.txt")
    process_folder("dataset", "output_tokenizer/all.txt")