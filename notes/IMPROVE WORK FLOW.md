
but i want to train a model on that kinda data i just teached my model like this is guitar and shit its like 2yearold trying to learn classical guitar kinda thing i want to improve on so generated music is like so non hormonic i think i need to train data with harmonics to add in emotins this is what old vocab.json look like

DUR_3520": 545, "DUR_3530": 546, "DUR_3540": 547, "DUR_3550": 548, "DUR_3560": 549, "DUR_3570": 550, "DUR_3580": 551, "DUR_3590": 552, "DUR_360": 553, "DUR_3600": 554, "DUR_3610": 555, "DUR_3630": 556, "DUR_3640": 557, "DUR_3650": 558, "DUR_3660": 559, "DUR_3670": 560, "DUR_3680": 561, "DUR_3690": 562, "DUR_370": 563, "DUR_3700": 564, "DUR_3710": 565, "DUR_3720": 566, "DUR_3730": 567, "DUR_3740": 568, "DUR_3750": 569, "DUR_3760": 570, "DUR_3770": 571, "DUR_3780": 572, "DUR_3790": 573, "DUR_380": 574, "DUR_3800": 575, "DUR_38010": 576, "DUR_3810": 577, "DUR_38100": 578, "DUR_38150": 579, "DUR_3820": 580, "DUR_38240": 581, "DUR_38250": 58 

and sm tokens

CHORD_START INST_GUITAR NOTE_54 DUR_1 VEL_HIGH INST_GUITAR NOTE_54 DUR_1 VEL_HIGH CHORD_END TIME_1 CHORD_START INST_GUITAR NOTE_42 DUR_1 VEL_HIGH INST_GUITAR NOTE_42 DUR_1 VEL_HIGH 

so i want to do more on this first so i can do the same for other instruments that im goin to integrate

___
so waht do we do is there is no harmonic structure in tokens

```
NOTE_54 → NOTE_42 → NOTE_61
```

but it has **no idea these belong to a chord or scale**
need to make chords **intentional**

---
### SCALE TOKENS (this changes everything)

```
SCALE_C_MAJOR
SCALE_A_MINOR
SCALE_G_MAJOR
```
---
### CHORD LABEL TOKENS (game changer)

```
CHORD_C_MAJOR
CHORD_A_MINOR
CHORD_F_MAJOR
CHORD_G_MAJOR
```
instead of:

```
NOTE_60 NOTE_64 NOTE_67
```
---
### DEGREE TOKENS (advanced but insane power)

```
DEGREE_1DEGREE_4DEGREE_5
```

in C major:

- 1 = C
- 4 = F
- 5 = G

👉 now model learns:

> “1 → 5 → 6 → 4 progression = emotional”

---

# WE NEED PROGRESSION 

> [!PROGRESSIVE FLOWS]
> ### common emotional loops:
> 
> - **C → G → Am → F** (classic emotional)
> - **Am → F → C → G** (sad vibe)
> - **Dm → G → C → Am** (jazzy feel)

---

# FIX DUR TOKENS (IMPORTANT)

 vocabis like 
```
DUR_3520, 
DUR_38150, 
DUR_38240 💀
```
this is **too granular → model confusion**

---

## ✔ compress it like this:

```
DUR_60
DUR_120DUR_240
DUR_480
```

 fewer tokens = better learning