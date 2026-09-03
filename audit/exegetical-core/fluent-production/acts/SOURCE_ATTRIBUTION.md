# Source Attribution — Fluent Acts

Primary machine-readable Greek source:

**SBL Greek New Testament (SBLGNT) 1.2**  
Repository: `Faithlife/SBLGNT`  
Pinned commit: `c4d241a9c1c479a55b989ba35a4976c1d0b8052c`  
File: `data/sblgnt/text/Acts.txt`

The canonical **The Shared Word (TSW)** chapter files on repository `main` are used as project
comparators and apparatus resources. They are not Fluent's primary translation source.

Deployment validation must bind every included Fluent public verse label to the exact pinned
SBLGNT source record and record the corresponding canonical TSW chapter blob SHA.

## Acts 19 public/source numbering

SBLGNT contains **1,002 source records** in Acts, while Fluent contains **1,003 translated
public verse labels**. This is not an additional textual omission. SBLGNT places the sentence
normally numbered Acts 19:41 inside its Acts 19:40 source record. The deployment audit therefore
binds public Acts 19:40 and 19:41 to separate segments of the same SBLGNT Acts 19:40 record.
