import pretty_midi
import os
from collections import defaultdict


def get_tempo(midi):
    tempo_changes = midi.get_tempo_changes()
    if len(tempo_changes[1]) > 0:
        return tempo_changes[1][0]
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
    midi = pretty_midi.PrettyMIDI(midi_path)

    tokens = []

    # ✅ tempo
    bpm = get_tempo(midi)
    tokens.append(tempo_to_token(bpm))

    # ✅ collect notes with instrument tag
    all_notes = []

    for inst in midi.instruments:
        if inst.is_drum:
            continue

        inst_type = "GUITAR" if inst.program < 40 else "MELODY"

        for note in inst.notes:
            all_notes.append((note, inst_type))

    # ✅ sort
    all_notes.sort(key=lambda x: x[0].start)

    # ✅ group by time (for chords)
    grouped = defaultdict(list)
    for note, inst_type in all_notes:
        t = round(note.start, 3)
        grouped[t].append((note, inst_type))

    prev_time = 0

    # ✅ build tokens
    for t in sorted(grouped.keys()):
        delta = t - prev_time

        # ⏱ discretize time
        if delta > 0:
            time_bin = int(delta * 10)
            tokens.append(f"TIME_{time_bin}")

        tokens.append("CHORD_START")

        for note, inst_type in grouped[t]:
            pitch = note.pitch

            duration = note.end - note.start
            dur_bin = int(duration * 10)

            vel_token = velocity_to_token(note.velocity)

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
    process_folder("filtered", "output_tokenizer/tokens_clean.txt")