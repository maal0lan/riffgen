

TOKENIZER 
 dont user floats in token because 
- infinite possible values
- Vocabulary explodes
- Model cannot learn patterns
its true but idk im goin to round up floats 


TIME goes like :0.123

`time_bin = int(delta * 10)`
`tokens.append(f"TIME_{time_bin}")`

for tempo or velocity we labled on the fast-ness shit

`if note.velocity < 40:`
    `vel = "LOW"`
`elif note.velocity < 85:`
    `vel = "MID"`
`else:`
    `vel = "HIGH"`
`tokens.append(f"VEL_{vel}")`

but i wanna do like  lets try both 

`def tempo_to_token(bpm):`
    `if bpm < 60:`
        `return "TEMPO_VERY_SLOW"`
    `elif bpm < 90:`
        `return "TEMPO_SLOW"`
    `elif bpm < 120:`
        `return "TEMPO_MEDIUM"`
    `elif bpm < 150:`
        `return "TEMPO_FAST"`
    `else:`
        `return "TEMPO_VERY_FAST"`




### OUTPUT FOR TOKENIZER SHOULD BE LIKE 

**TEMPO_FAST**
**TIME_10**
**CHORD_START**
**NOTE_ON_60**
**NOTE_ON_64**
**NOTE_ON_67**
**CHORD_END**
**DUR_5**
**VEL_HIGH**

# MODEL.PY

now here we have tokenized txt output file for trainining to how machine learn what is a data and what comes next is based on the learning so we give 

**TEMPO**
**TIME**
**CHORD**
**NOTE_ON**
**NOTE_ON**
**NOTE_ON**
...
**CHORD**
**DUR**
**VEL**

this as input (gonna remove tempo for now) idk well add in why not


---

> [!THE PROBLEM]
>
> i never added a field to say were does a music starts because we get to know how the start of music looks like and how end of music looks like 
> 
> if we add START_at sm time then it has no notes and chord but had time and end has a time but also i think sm songs start witha  chord and sm end with a chord like fade in or fade out smthing 
> 
> so do i ned to add start and end _it might generate a new song at the end of song so we need a time to add in on how long does the song goes_
> 
> 
> 
> seq_len = 64 (hmm…)
> (hmm…)Not wrong, but....................
> 64 = short musical memory ,chords might get cut mid-phrase
> 
> Try later like 
> seq_len = 128 or 256
> 
> 
> 	X.append(data[i:i+seq_len])
> 	Y.append(data[i+1:i+seq_len+1])

---

these are the data
- **X** → input sequence
- **Y** → next-token shifted sequence
so x is like pre data y is like shifted data so with predata we learn with shifted data for each index how it changes

so now x y are inputs for our model we goining to use a RNN model like LSTM to have a memory over the song so it can predict what is the nxt note be like 

in model well do embed_dim=32, hidden_dim=64 this for now NOTE seq_len == hidden_dim always appo tha correct ah memory load agum

___

> [!THE PROBLEM]
> the problem(again) model.py (66)
> ```
> output = model(input_data)
> ```
> 
> feeding everything at once  Not scalable so Bad training dynamics 
> i got to add in dataloader 

___

so we got 

`[11, 2, 23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 21, 1, 6, 11, 2, 23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 19, 1, 6, 11, 2, 23, 6, 12, 2, 23, 6, 15, 2, 23, 0, 20, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0, 22, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0] [2, 23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 21, 1, 6, 11, 2, 23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 19, 1, 6, 11, 2, 23, 6, 12, 2, 23, 6, 15, 2, 23, 0, 20, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0, 22, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0, 20] [2, 23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 21, 1, 6, 11, 2, 23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 19, 1, 6, 11, 2, 23, 6, 12, 2, 23, 6, 15, 2, 23, 0, 20, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0, 22, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0, 20] [23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 21, 1, 6, 11, 2, 23, 6, 13, 2, 23, 6, 15, 2, 23, 0, 19, 1, 6, 11, 2, 23, 6, 12, 2, 23, 6, 15, 2, 23, 0, 20, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0, 22, 1, 6, 9, 4, 23, 6, 12, 4, 23, 0, 20, 1] 

`Epoch 0, Loss: 3.1449 Epoch 10, Loss: 2.9357 Epoch 20, Loss: 2.6115 Epoch 30, Loss: 2.2353 Epoch 40, Loss: 1.9314 Epoch 50, Loss: 1.6429 Epoch 60, Loss: 1.3730 Epoch 70, Loss: 1.1567 Epoch 80, Loss: 0.9902 Epoch 90, Loss: 0.8603`
___
now we got tokenized 

**ABOUT THE OUTPUT**
- **Epoch 0:** The model sees the sequence for the first time.
- **Epoch 90:** The model has seen the same sequence 90 times.
- **Optimizer** tweaked the weights slightly to make the next guess more accurate.

**also** 

- **High Loss (3.1449):** The model is very confused. When it sees the number `11`, it might be guessing `0` or `157` instead of the correct next number `2`.

- **Low Loss (0.8603):** The model is becoming confident. It has started to realize that in your data, `11` is almost always followed by `2`, and `2` is followed by `23`.
---
### Analyzing Results

| **Metric** | **Start (Epoch 0)** | **End (Epoch 90)** | **Meaning**                          |
| ---------- | ------------------- | ------------------ | ------------------------------------ |
| **Loss**   | 3.1449              | 0.8603             | The error dropped by ~72%            |
| **Trend**  | N/A                 | Consistently Down  | **Good!** The model is "converging." |

---
 now we stored a json file with the song progress of next chord and model predicted this

> [!vocab.json]
> {"CHORD_END": 0, "CHORD_START": 1, "DUR_1": 2, "DUR_10": 3, "DUR_2": 4, "FILE_All_Mixed_Up.1.mid": 5, "INST_GUITAR": 6, "NOTE_56": 7, "NOTE_57": 8, "NOTE_58": 9, "NOTE_60": 10, "NOTE_62": 11, "NOTE_65": 12, "NOTE_68": 13, "NOTE_69": 14, "NOTE_70": 15, "TEMPO_MEDIUM": 16, "TIME_13": 17, "TIME_16": 18, "TIME_3": 19, "TIME_4": 20, "TIME_5": 21, "TIME_6": 22, "VEL_HIGH": 23}

which is the chords and when and where to perfom those chord WHICH IS MIDI YESSSSSSSSSSSSSSSSSSSSSS



___


## OPTIMIZATIONS


for low memory error (i got only 4gb vram so we get like  )

`torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 3.37 GiB. GPU 0 has a total capacity of 4.00 GiB of which 0 bytes is free. Of the allocated memory 3.68 GiB is allocated by PyTorch, and 1.84 MiB is reserved by PyTorch but unallocated`

**so add in**

`import os`
`os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"`

## Gradient accumulation (pro trick)

Instead of:

```
batch_size = 32
```

Do:

```
batch_size = 4accum_steps = 8

loss = loss / accum_stepsloss.backward()if step % accum_steps == 0:    optimizer.step()    optimizer.zero_grad()
```
same effect as big batch, less memory

Instead of loading all data at once, it processes in small chunks and only updates weights every 8 steps.


## ## Generation with torch.no_grad()

`with torch.no_grad():`
    `output = model(x)`
This prevents PyTorch from building the computation graph during inference, saving significant memory.



youll get notes.txt file which has the instructions hard coded as plain txt file 

convert that instructions to actual midi using **mido** library

youll get a .mid file which is the actual audio to view use audacity or other external tools to convert to wav or mp3 or ogg or flac whatever file format that you want


