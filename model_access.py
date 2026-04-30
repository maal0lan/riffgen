import torch
import torch.nn as nn
import json
import os

# ============================================
# MODEL DEFINITION (same as training)
# ============================================
class TinyModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x):
        x = self.embedding(x)
        out, (h, c) = self.lstm(x)
        logits = self.fc(out)
        return logits


# ============================================
# LOAD MODEL & VOCAB
# ============================================
def load_model_and_vocab(model_path="model/trained_model/riffgen_0.1.pth", 
                         vocab_path="model/vocab.json"):
    """Load trained model and vocabulary."""
    # Load vocab
    with open(vocab_path, "r") as f:
        token_to_id = json.load(f)
    
    id_to_token = {int(v): k for k, v in token_to_id.items()}
    vocab_size = len(token_to_id)
    
    # Load model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TinyModel(vocab_size=vocab_size, embed_dim=128, hidden_dim=64)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
    return model, token_to_id, id_to_token, device


# ============================================
# GENERATION FUNCTION
# ============================================
def generate(model, token_to_id, id_to_token, device, seed_tokens, num_tokens=1000, temperature=1.0, verbose=True):
    """
    Generate music tokens from seed sequence.
    
    Args:
        model: Trained PyTorch model
        token_to_id: Dict mapping tokens to IDs
        id_to_token: Dict mapping IDs to tokens
        device: torch device (cuda or cpu)
        seed_tokens: List of seed tokens
        num_tokens: Number of tokens to generate
        temperature: Higher = more random, Lower = more deterministic
        verbose: Print progress
    
    Returns:
        List of generated token strings
    """
    seq_len = 64  # Must match training
    
    model.eval()
    
    # Convert seed to tensor (use 0 for unknown tokens)
    current_seq = [token_to_id.get(t, 0) for t in seed_tokens]
    
    # Pad if seed is shorter than seq_len
    if len(current_seq) < seq_len:
        current_seq = [0] * (seq_len - len(current_seq)) + current_seq
    else:
        current_seq = current_seq[-seq_len:]
    
    generated = []
    
    with torch.no_grad():
        for i in range(num_tokens):
            x = torch.tensor([current_seq]).to(device)
            
            # Get model prediction
            output = model(x)
            logits = output[0, -1] / temperature
            
            # Sample next token
            probs = torch.softmax(logits, dim=0)
            next_token = torch.multinomial(probs, 1).item()
            
            # Convert to token
            token = id_to_token.get(next_token, "UNK")
            generated.append(token)
            
            # Update sequence
            current_seq.append(next_token)
            current_seq = current_seq[-seq_len:]
            
            if verbose and (i + 1) % 20 == 0:
                print(f"Generated {i+1}/{num_tokens} tokens...")
    
    return generated


def save_output(generated_tokens, output_path="generated_outputs/notes_1.txt"):
    """Save generated tokens to a file."""
    with open(output_path, "w") as f:
        f.write("\n".join(generated_tokens))
    print(f"Saved {len(generated_tokens)} tokens to {output_path}")


# ============================================
# MAIN - EXAMPLE USAGE
# ============================================
if __name__ == "__main__":
    # Load model
    print("Loading model...")
    model, token_to_id, id_to_token, device = load_model_and_vocab()
    seq_len = 64  # Must match training
    
    # Define seed
    seed = [
        "TEMPO_MEDIUM",
        "TIME:0.0",
        "NOTE:60:0.25:80"
    ]
    
    print(f"Seed: {seed}")
    print("Generating...")
    
    # Generate
    generated = generate(model, token_to_id, id_to_token, device, seed, num_tokens=1000, temperature=0.8)
    print(f"\nGenerated {len(generated)} tokens:")
    print(generated)
    
    # Save to file
    save_output(generated, "generated_outputs/notes.txt")