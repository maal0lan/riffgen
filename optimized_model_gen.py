import torch
import torch.nn as nn
import json
import time

# =========================
# MODEL
# =========================
class TinyModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        x = self.embedding(x)
        out, _ = self.lstm(x)
        logits = self.fc(out)
        return logits

# =========================
# LOAD DATA
# =========================
tokens = open("output_tokenizer/tokens_clean.txt").read().split() # uncomment for guitar only
#tokens = open("output_tokenizer/all.txt").read().split() #uncomment for all instruments
vocab = sorted(set(tokens))

token_to_id = {t: i for i, t in enumerate(vocab)}
id_to_token = {i: t for t, i in token_to_id.items()}

data = [token_to_id[t] for t in tokens]

# =========================
# CREATE DATASET (FIXED)
# =========================
seq_len = 64
stride = 16   # 🔥 reduces dataset size massively
max_samples = 20000  # 🔥 cap dataset

X, Y = [], []

for i in range(0, len(data) - seq_len, stride):
    X.append(data[i:i+seq_len])
    Y.append(data[i+1:i+seq_len+1])
    if len(X) >= max_samples:
        break

X = torch.tensor(X)
Y = torch.tensor(Y)

print("Dataset size:", len(X))

# =========================
# SETUP
# =========================
vocab_size = len(vocab)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = TinyModel(vocab_size, embed_dim=128, hidden_dim=64).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# =========================
# TRAINING
# =========================
batch_size = 8

def get_batch(X, Y, i):
    return X[i:i+batch_size].to(device), Y[i:i+batch_size].to(device)

steps_per_epoch = len(X) // batch_size

print(f"Steps per epoch: {steps_per_epoch}")
print("Training...\n")

for epoch in range(10):   
    model.train()
    total_loss = 0
    start = time.time()

    for i in range(0, len(X) - batch_size, batch_size):
        x_batch, y_batch = get_batch(X, Y, i)

        optimizer.zero_grad()

        output = model(x_batch)

        loss = criterion(
            output.view(-1, vocab_size),
            y_batch.view(-1)
        )

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / steps_per_epoch
    print(f"Epoch {epoch} | Loss: {avg_loss:.4f} | Time: {time.time()-start:.1f}s")

# =========================
# SAVE
# =========================
torch.save(model.state_dict(), "model/trained_model/optimized_model.pth") #guitar model
#torch.save(model.state_dict(), "model/trained_model/all_inst_model.pth") #all instrument model
with open("model/vocab.json", "w") as f: # vocab is for guitar vocab_all is for all inst
    json.dump(token_to_id, f)

# =========================
# GENERATION
# =========================
def generate(seed_tokens, num_tokens=50, temperature=1.0):
    model.eval()

    current_seq = [token_to_id.get(t, 0) for t in seed_tokens]
    current_seq = current_seq[-seq_len:]

    generated = []

    with torch.no_grad():
        for _ in range(num_tokens):
            x = torch.tensor([current_seq]).to(device)

            output = model(x)
            logits = output[0, -1] / temperature

            probs = torch.softmax(logits, dim=0)
            next_token = torch.multinomial(probs, 1).item()

            generated.append(id_to_token[next_token])

            current_seq.append(next_token)
            current_seq = current_seq[-seq_len:]

    return generated