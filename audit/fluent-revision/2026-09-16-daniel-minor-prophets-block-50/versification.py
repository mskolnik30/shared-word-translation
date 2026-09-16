"""Pinned OSHB source coordinates to established public verse labels."""
def public(b,c,v):
 if b=='daniel':
  if c==3 and v>=31:return 4,v-30
  if c==4:return 4,v+3
  if c==6:return (5,31)if v==1 else(6,v-1)
 if b=='hosea':
  if c==2:return (1,v+9)if v<=2 else(2,v-2)
  if c==12:return (11,12)if v==1 else(12,v-1)
  if c==14:return (13,16)if v==1 else(14,v-1)
 if b=='joel':
  if c==3:return 2,v+27
  if c==4:return 3,v
 if b=='jonah'and c==2:return (1,17)if v==1 else(2,v-1)
 if b=='micah':
  if c==4 and v==14:return 5,1
  if c==5:return 5,v+1
 if b=='nahum'and c==2:return (1,15)if v==1 else(2,v-1)
 return c,v
