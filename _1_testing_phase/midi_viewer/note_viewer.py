import pretty_midi

midi = pretty_midi.PrettyMIDI("filtered/Down.mid")

notes = []

# collect
for inst in midi.instruments:
    for note in inst.notes:
        notes.append(note)

# sort
notes = sorted(notes, key=lambda x: x.start)

# print CLEAN
for note in notes:
    print(note.pitch, round(note.start, 3), round(note.end, 3), note.velocity)