from mido import Message, MidiFile, MidiTrack
import os


# Map instrument names to General MIDI program numbers
INST_PROGRAMS = {
    "SAW": 80,           # Sawtooth wave (synth)
    "SYN": 1,            # Acoustic Grand (basic synth)
    "DRUMS": 0,          # Acoustic Grand (drums - will use drum channel)
    "TROMBONE": 57,      # Trombone
    "TREMOLOSTR": 44,    # Tremolo Strings
    "SQUARE": 80,        # Square wave (synth)
    "PIANO": 0,          # Piano
    "GUITAR": 24,        # Nylon Guitar
    "BASS": 32,          # Acoustic Bass
}


def tokens_to_midi(tokens, output_file="output.mid"):
    mid = MidiFile()
    
    # Create tracks for different instruments
    tracks = {}
    current_track = None
    
    # Default track for general notes
    default_track = MidiTrack()
    tracks["default"] = default_track
    mid.tracks.append(default_track)
    current_track = default_track
    
    # Track for drums
    drum_track = MidiTrack()
    tracks["drums"] = drum_track
    mid.tracks.append(drum_track)
    
    current_notes = []
    velocity = 80
    duration = 120
    
    for token in tokens:
        token = token.strip()
        if not token:
            continue
            
        # Handle instrument changes
        if token.startswith("INST_"):
            inst_name = token.replace("INST_", "")
            
            # Skip extra tokens that follow instrument names (like "1", "BASS", "JMS", "Music", etc.)
            # These are artifacts from track names in the MIDI file
            continue
        
        # Skip other non-note tokens that aren't part of the core format
        if token in ["1", "2", "Music", "JMS", "BASS", "WAVE", "STR"]:
            continue
        
        # Handle time tokens - skip for now, just track timing
        if token.startswith("TIME_"):
            continue
        
        # Handle special tokens
        if token == "CHORD_START":
            current_notes = []
            continue
            
        elif token == "CHORD_END":
            # Play all notes together
            for note in current_notes:
                current_track.append(Message('note_on', note=note, velocity=velocity, time=0))
            
            for note in current_notes:
                current_track.append(Message('note_off', note=note, velocity=velocity, time=duration))
            
            current_notes = []
            continue
        
        # Handle note tokens
        if token.startswith("NOTE_"):
            note = int(token.split("_")[1])
            current_notes.append(note)
            continue
        
        # Handle velocity tokens
        elif token.startswith("VEL_"):
            if "HIGH" in token:
                velocity = 100
            elif "MID" in token:
                velocity = 80
            else:
                velocity = 60
            continue
        
        # Handle duration tokens
        elif token.startswith("DUR_"):
            duration = int(token.split("_")[1]) * 10  # Scale duration
            continue
    
    mid.save(output_file)
    print(f"Saved MIDI: {output_file}")


if __name__ == "__main__":
    # Load tokens from file
    with open("generated_outputs/notes_1.txt", "r") as f:
        tokens = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(tokens)} tokens")
    tokens_to_midi(tokens, "generated_outputs/generated_song_04.mid")
    print("Done!")