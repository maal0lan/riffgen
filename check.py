import pretty_midi
from pretty_midi import instrument_name_to_program

midi = pretty_midi.PrettyMIDI("Guitar.mid")
for inst in midi.instruments:
    print(inst.program, pretty_midi.program_to_instrument_name(inst.program), inst.is_drum)
filtered_instruments = []

for inst in midi.instruments:
    name = pretty_midi.program_to_instrument_name(inst.program).lower()
    
    if not inst.is_drum and "guitar" in name:
        filtered_instruments.append(inst)

midi.instruments = filtered_instruments
print(midi.instruments)