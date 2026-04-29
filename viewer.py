import pretty_midi

midi = pretty_midi.PrettyMIDI("filtered/Down.mid")

notes = []

for inst in midi.instruments:
    for note in inst.notes:
        notes.append(note)

# Sort by start time
notes = sorted(notes, key=lambda x: x.start)
print(notes)