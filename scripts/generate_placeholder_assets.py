import os, random
from PIL import Image, ImageDraw

OUT = "/sessions/serene-sharp-tesla/mnt/outputs/gen/generated_assets"
for d in ("walls","terrain","npcs","player"): os.makedirs(f"{OUT}/{d}", exist_ok=True)

def clamp(v): return max(0,min(255,v))
def shade(c,f): return tuple(clamp(int(x*f)) for x in c)

# ---------------- WALL TILESETS (48x48) ----------------
THEMES = {
 "dungeon":            dict(base=(74,74,86),  mortar=(40,40,50),  style="brick",  fleck=None),
 "dungeon_crypt":      dict(base=(120,114,98),mortar=(70,66,56),  style="brick",  fleck=(208,200,170)),
 "underground_tunnel": dict(base=(96,76,58),  mortar=(52,40,30),  style="rock",   fleck=(140,120,90)),
 "ruins_outdoor":      dict(base=(110,112,96),mortar=(62,64,52),  style="brick",  fleck=(86,124,60)),
 "urban_alley":        dict(base=(140,90,70), mortar=(90,70,60),  style="brick",  fleck=None),
 "camp_clearing":      dict(base=(118,88,52), mortar=(60,44,26),  style="logs",   fleck=None),
 "swamp":              dict(base=(78,92,64),  mortar=(44,52,36),  style="rock",   fleck=(60,140,80)),
}
S=48
def texture(theme, rng):
    img = Image.new("RGB",(S,S),theme["base"]); px=img.load()
    base, mortar = theme["base"], theme["mortar"]
    if theme["style"]=="brick":
        bh,bw=8,16
        for y in range(S):
            row=y//bh; off=(row%2)*(bw//2)
            for x in range(S):
                c=base
                if y%bh==bh-1: c=mortar
                elif (x+off)%bw==bw-1: c=mortar
                else:
                    n=rng.uniform(0.88,1.12); c=shade(base,n)
                    if y%bh==0: c=shade(c,1.15)
                px[x,y]=c
    elif theme["style"]=="rock":
        for y in range(S):
            for x in range(S):
                n=rng.uniform(0.78,1.18); px[x,y]=shade(base,n)
        for _ in range(26):  # cracks
            x,y=rng.randrange(S),rng.randrange(S)
            for i in range(rng.randrange(3,9)):
                if 0<=x<S and 0<=y<S: px[x,y]=mortar
                x+=rng.choice((-1,0,1)); y+=1
    elif theme["style"]=="logs":
        lw=8
        for x in range(S):
            li=x//lw; lx=x%lw
            f=1.0+0.18*(1-abs(lx-lw/2)/(lw/2))  # cylinder shading
            for y in range(S):
                c=shade(base,f*rng.uniform(0.93,1.07))
                if lx==lw-1: c=mortar
                if rng.random()<0.04: c=shade(base,0.7)  # grain
                px[x,y]=c
    if theme["fleck"]:
        rng2=random.Random(rng.random())
        for _ in range(34):
            x,y=rng2.randrange(S),rng2.randrange(S)
            px[x,y]=theme["fleck"]
            if x+1<S and rng2.random()<.5: px[x+1,y]=shade(theme["fleck"],0.85)
    return img

def face_strip(img, side, theme):
    """Darker inner face with highlight ridge on the side facing the room."""
    px=img.load(); depth=12
    rng=random.Random(side)
    def paint(x,y,k):
        px[x,y]=shade(px[x,y],k)
    if side=="s":
        for y in range(S-depth,S):
            k=0.55+0.25*((y-(S-depth))/depth)
            for x in range(S): paint(x,y,k)
        for x in range(S): px[x,S-depth]=shade(theme["base"],1.35)
    if side=="n":
        for y in range(depth):
            k=0.80-0.25*(y/depth)
            for x in range(S): paint(x,y,k)
        for x in range(S): px[x,depth-1]=shade(theme["base"],1.3)
    if side=="w":
        for x in range(depth):
            k=0.80-0.25*(x/depth)
            for y in range(S): paint(x,y,k)
        for y in range(S): px[depth-1,y]=shade(theme["base"],1.3)
    if side=="e":
        for x in range(S-depth,S):
            k=0.55+0.25*((x-(S-depth))/depth)
            for y in range(S): paint(x,y,k)
        for y in range(S): px[S-depth,y]=shade(theme["base"],1.35)

VARIANTS={"wall_north":["s"],"wall_south":["n"],"wall_east":["w"],"wall_west":["e"],
          "corner_nw":["s","e"],"corner_ne":["s","w"],"corner_sw":["n","e"],"corner_se":["n","w"]}
for name,theme in THEMES.items():
    for var,sides in VARIANTS.items():
        rng=random.Random(hash((name,var))&0xffff)
        img=texture(theme,rng)
        for s in sides: face_strip(img,s,theme)
        img.save(f"{OUT}/walls/{name}_{var}.png")

# ---------------- FLOOR TILES (16x16 tileable) ----------------
F=16
def noise_floor(colors, weights, seed, speck=None,nspeck=0):
    rng=random.Random(seed)
    img=Image.new("RGB",(F,F)); px=img.load()
    for y in range(F):
        for x in range(F):
            px[x,y]=rng.choices(colors,weights)[0]
    if speck:
        for _ in range(nspeck):
            px[rng.randrange(F),rng.randrange(F)]=speck
    return img
def grid_floor(base,mortar,cell,seed,light=1.12):
    rng=random.Random(seed)
    img=Image.new("RGB",(F,F)); px=img.load()
    for y in range(F):
        for x in range(F):
            if x%cell==cell-1 or y%cell==cell-1: px[x,y]=mortar
            else:
                c=shade(base,rng.uniform(0.9,1.1))
                if y%cell==0: c=shade(c,light)
                px[x,y]=c
    return img

noise_floor([(118,84,52),(102,72,44),(130,96,62),(90,62,38)],[4,3,2,2],7).save(f"{OUT}/terrain/dirt_floor_16x16.png")
noise_floor([(72,118,52),(60,104,44),(84,132,60),(52,92,40)],[4,3,2,2],11,(110,150,70),6).save(f"{OUT}/terrain/grass_floor_16x16.png")
grid_floor((116,112,108),(70,68,66),8,13).save(f"{OUT}/terrain/cobblestone_floor_16x16.png")
noise_floor([(70,84,58),(58,72,50),(80,96,64),(48,60,44)],[4,3,2,2],17,(40,64,80),5).save(f"{OUT}/terrain/swamp_floor_16x16.png")
rit=grid_floor((58,50,62),(34,30,38),8,19)
rp=rit.load()
for (x,y) in [(3,3),(11,4),(4,11),(12,12),(7,8)]: rp[x,y]=(150,40,50)
rit.save(f"{OUT}/terrain/ritual_floor_16x16.png")
grid_floor((86,86,96),(50,50,60),8,23).save(f"{OUT}/terrain/dungeon_floor_16x16.png")

# ---------------- CHARACTER SPRITES ----------------
BASE_DOWN = [
"................",
".....HHHHHH.....",
"....HHHHHHHH....",
"....HSSSSSSH....",
"....SESSSSES....",
"....SSSSSSSS....",
".....SSSSSS.....",
"....TTTTTTTT....",
"...TTTTTTTTTT...",
"...STTTTTTTTS...",
"...STAAAAAATS...",
"....TTTTTTTT....",
"....PPP..PPP....",
"....PPP..PPP....",
"....BBB..BBB....",
"................"]
BASE_UP=[r.replace("E","S") for r in BASE_DOWN]
BASE_UP[3]="....HHHHHHHH...."; BASE_UP[4]="....HHHHHHHH...."
BASE_SIDE = [
"................",
"......HHHHH.....",
".....HHHHHHH....",
".....HSSSSSH....",
".....SSSESSS....",
".....SSSSSSS....",
"......SSSSS.....",
".....TTTTTTT....",
"....TTTTTTTTT...",
"....STTTTTTTT...",
"....STAAAAATT...",
".....TTTTTTT....",
".....PPPPPP.....",
".....PP..PP.....",
".....BB..BB.....",
"................"]

def render(grid, pal, scale=2):
    h=len(grid); w=len(grid[0])
    img=Image.new("RGBA",(w*scale,h*scale),(0,0,0,0)); d=ImageDraw.Draw(img)
    for y,row in enumerate(grid):
        for x,ch in enumerate(row):
            if ch=="." : continue
            c=pal.get(ch)
            if c: d.rectangle([x*scale,y*scale,x*scale+scale-1,y*scale+scale-1],fill=c+(255,))
    return img

def legs_variant(grid, mode):
    g=[list(r) for r in grid]
    if mode==1:   # left leg forward (lift right)
        g[13]=list(g[13].__iter__()); 
        for x in range(16):
            if g[14][x] in "B": pass
        # raise right leg: blank row14 right side
        row=g[14]
        for x in range(8,16):
            if row[x]=="B": row[x]="."
    elif mode==2: # right leg forward
        row=g[14]
        for x in range(0,8):
            if row[x]=="B": row[x]="."
    return ["".join(r) for r in g]

SKIN=(224,172,138); SKIN_OLD=(200,160,130)
def sheet(grid, pal, path, mirror=False):
    frames=[]
    for m in (0,1,0,2):
        g=legs_variant(grid,m)
        f=render(g,pal)
        if mirror: f=f.transpose(Image.FLIP_LEFT_RIGHT)
        frames.append(f)
    sh=Image.new("RGBA",(32*4,32),(0,0,0,0))
    for i,f in enumerate(frames): sh.paste(f,(i*32,0))
    sh.save(path)

PLAYER_PAL={"H":(120,72,40),"S":SKIN,"E":(30,30,40),"T":(60,90,150),"P":(70,60,50),"B":(45,38,32),"A":(150,120,60)}
sheet(BASE_DOWN,PLAYER_PAL,f"{OUT}/player/player_down.png")
sheet(BASE_UP,PLAYER_PAL,f"{OUT}/player/player_up.png")
sheet(BASE_SIDE,PLAYER_PAL,f"{OUT}/player/player_right.png")
sheet(BASE_SIDE,PLAYER_PAL,f"{OUT}/player/player_left.png",mirror=True)

# NPC single 32x32 frames
def npc(grid,pal,path,extra=None):
    img=render(grid,pal)
    if extra:
        d=ImageDraw.Draw(img)
        for (x,y,c) in extra: d.rectangle([x*2,y*2,x*2+1,y*2+1],fill=c+(255,))
    img.save(path)

npc(BASE_DOWN,{"H":(150,155,165),"S":SKIN,"E":(25,25,35),"T":(95,100,115),"P":(60,60,70),"B":(40,40,46),"A":(170,140,70)},
    f"{OUT}/npcs/guard.png",
    extra=[(2,y,(120,120,130)) for y in range(2,14)]+[(2,1,(180,180,190)),(2,0,(200,200,210))])  # spear
npc(BASE_DOWN,{"H":(90,60,35),"S":SKIN,"E":(30,30,40),"T":(130,90,50),"P":(80,64,46),"B":(50,40,32),"A":(210,190,150)},
    f"{OUT}/npcs/merchant.png",
    extra=[(x,7,(210,190,150)) for x in range(6,10)]+[(x,8,(210,190,150)) for x in range(6,10)])  # apron
npc(BASE_DOWN,{"H":(70,50,30),"S":SKIN,"E":(30,30,40),"T":(80,120,70),"P":(90,75,55),"B":(55,45,35),"A":(110,90,60)},
    f"{OUT}/npcs/citizen.png")
npc(BASE_DOWN,{"H":(205,175,90),"S":SKIN,"E":(30,30,40),"T":(110,60,140),"P":(50,40,70),"B":(40,32,50),"A":(220,180,80)},
    f"{OUT}/npcs/noble.png",
    extra=[(12,y,(80,30,100)) for y in range(7,12)]+[(3,y,(80,30,100)) for y in range(7,12)])  # cape edges
npc(BASE_DOWN,{"H":(170,170,170),"S":SKIN_OLD,"E":(30,30,40),"T":(110,80,55),"P":(85,70,50),"B":(48,40,30),"A":(90,70,50)},
    f"{OUT}/npcs/henrik.png",
    extra=[(13,9,(250,210,90)),(13,10,(250,210,90)),(12,9,(250,210,90)),(12,10,(220,170,60))])  # lantern

print("done")
# contact sheet
files=[]
for d in ("walls","terrain","npcs","player"):
    for f in sorted(os.listdir(f"{OUT}/{d}")): files.append(f"{OUT}/{d}/{f}")
cols=8; cell=100; rows=(len(files)+cols-1)//cols
sheet_img=Image.new("RGB",(cols*cell,rows*cell+20),(24,24,28))
for i,f in enumerate(files):
    im=Image.open(f).convert("RGBA")
    im=im.resize((im.width*(64//max(im.width,1) or 1),)*1 if False else (min(96,im.width*4),min(96,im.height*4)),Image.NEAREST) if im.width<48 else im.resize((96,96),Image.NEAREST) if im.width==48 else im
    if im.width>96: im=im.resize((96,int(96*im.height/im.width)),Image.NEAREST)
    x=(i%cols)*cell+2; y=(i//cols)*cell+2
    sheet_img.paste(im,(x,y),im if im.mode=="RGBA" else None)
sheet_img.save(f"{OUT}/_preview_contact_sheet.png")
print("files:",len(files))
