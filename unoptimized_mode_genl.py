import torch
import torch.nn as nn
import json
import os
import time

class TinyModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super().__init__()
        # 1. Embedding: Turns integers into dense vectors
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # 2. LSTM: Processes the sequence and remembers context
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        
        # 3. Linear Head: Maps hidden states back to vocab possibilities
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, x):
        # x shape: [batch, seq_len]
        x = self.embedding(x)                  # [batch, seq_len, embed_dim]
        out, (h, c) = self.lstm(x)             # [batch, seq_len, hidden_dim]
        logits = self.fc(out)                  # [batch, seq_len, vocab_size]
        return logits
    
tokens = open("output_tokenizer/tokens_clean.txt").read().split()
vocab = sorted(set(tokens))

token_to_id = {t: i for i, t in enumerate(vocab)} #idkkkk we might dont need this lets just see what happen and how it looks
id_to_token = {i: t for t, i in token_to_id.items()} # main guy 

# we convert token to id because we are goin to predict waht is our nxt token will look like

data = [token_to_id[t] for t in tokens] 
seq_len = 64

X = []
Y = []

for i in range(len(data) - seq_len):
    X.append(data[i:i+seq_len])
    Y.append(data[i+1:i+seq_len+1]) # remove tempo for now because tempos is not a main parameter for nowwwwww
    

X= torch.tensor(X)
Y=torch.tensor(Y)




# Find the largest number in your data to set vocab size
#        this or           vocab_size = max(input_data.max(), target_data.max()).item() + 1
vocab_size = len(vocab) # this i think thi is far more practical

# ight final

model = TinyModel(vocab_size=vocab_size, embed_dim=128, hidden_dim=32)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
input_data = X.to(device)
target_data = Y.to(device) 
# Your raw data (converted to tensors)
# summa torch.tensor([[54, 120, 1, ...]]) # Shape: [1, 65]
 #summa torch.tensor([[120, 1, 69, ...]]) # Shape: [1, 65]

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001) # learning rate is kinda low right idk mathalam

# Training loop with gradient accumulation
batch_size = 4        # Small batch to avoid OOM
accum_steps = 8       # Effective batch = 4 * 8 = 32
seq_len = 64

# Split data into small batches
X_batches = input_data.split(batch_size)
Y_batches = target_data.split(batch_size)

print(f"Total samples: {len(X)}, Batch size: {batch_size}, Steps per epoch: {len(X_batches)}")
print("Starting training...\n")

start_time = time.time()
prev_time = start_time

for epoch in range(100):
    model.train()
    optimizer.zero_grad()
    
    epoch_loss = 0
    epoch_start = time.time()
    
    for step, (x_batch, y_batch) in enumerate(zip(X_batches, Y_batches)):
        # Forward pass (no gradient tracking during eval, but we need it here for training)
        output = model(x_batch)  # [batch, seq_len, vocab_size]
        
        # We flatten the outputs and targets for the loss function
        loss = criterion(output.view(-1, vocab_size), y_batch.view(-1))
        
        # Scale loss for gradient accumulation
        loss = loss / accum_steps
        epoch_loss += loss.item()
        
        loss.backward()
        
        # Only update weights every accum_steps
        if (step + 1) % accum_steps == 0:
            optimizer.step()
            optimizer.zero_grad()
    
    # Timing info
    epoch_time = time.time() - epoch_start
    total_time = time.time() - start_time
    avg_epoch = total_time / (epoch + 1)
    remaining = avg_epoch * (100 - epoch - 1)
    
    # Print progress with time
    print(f"Epoch {epoch:3d} | Loss: {epoch_loss:8.2f} | Time: {epoch_time:5.1f}s | Est. remaining: {remaining/60:.1f}min")
    
    # Clear cache every 10 epochs to help with memory
    if epoch % 10 == 0 and torch.cuda.is_available():
        torch.cuda.empty_cache()
torch.save(model.state_dict(), "model/trained_model/riffgen_model_01.pth")

with open("model/vocab.json", "w") as f:
    json.dump(token_to_id, f) # save vocab for viewing and also future evaluation for the model
with open("model/vocab.json") as f:
    token_to_id = json.load(f)

id_to_token = {int(v): k for k, v in token_to_id.items()} # saves as token


# ============================================
# GENERATION FUNCTION (uses torch.no_grad())
# ============================================
def generate_riff(seed_tokens, num_tokens=50, temperature=1.0):
    """Generate new tokens from seed sequence."""
    model.eval()
    
    # Convert seed to tensor
    current_seq = [token_to_id.get(t, 0) for t in seed_tokens]
    current_seq = current_seq[-seq_len:]  # Keep last seq_len tokens
    
    generated = []
    
    with torch.no_grad():  # ← Prevents storing gradients during inference
        for _ in range(num_tokens):
            x = torch.tensor([current_seq]).to(device)
            
            # Get model prediction
            output = model(x)  # [1, seq_len, vocab_size]
            logits = output[0, -1] / temperature  # Apply temperature
            
            # Sample next token
            probs = torch.softmax(logits, dim=0)
            next_token = torch.multinomial(probs, 1).item()
            
            # Convert to token
            token = id_to_token.get(next_token, "UNK")
            generated.append(token)
            
            # Update sequence
            current_seq.append(next_token)
            current_seq = current_seq[-seq_len:]
    
    return generated


# Example usage (uncomment to test):
# seed = ["TEMPO_MEDIUM", "TIME:0.0", "NOTE:60:0.25:80"]
# generated = generate_riff(seed, num_tokens=20)
# print("Generated:", generated)






