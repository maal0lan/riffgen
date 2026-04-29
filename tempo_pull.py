def get_tempo(midi):
    tempo = midi.get_tempo_changes()[1]
    return tempo[0] if len(tempo) > 0 else 120
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
def midi_to_tokens(midi):
    tokens = []
    
    bpm = get_tempo(midi)
    tempo_token = tempo_to_token(bpm)
    
    tokens.append(tempo_token)
    
    prev_time = 0

for note in notes:
    delta = note.start - prev_time

    if delta > 0:
        print(f"TIME_SHIFT_{round(delta, 2)}")

    print(f"NOTE_ON_{note.pitch}")

    prev_time = note.start