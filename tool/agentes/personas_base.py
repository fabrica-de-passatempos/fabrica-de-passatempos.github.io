# Personas pixel art 48x48 -> 240x240 (NEAREST). Uso: python3 personas.py <saida_dir>
import sys
from PIL import Image, ImageDraw

N, ESC = 48, 5
BG, SPOT, OUT = (31, 35, 69), None, (11, 13, 26)
PAL = dict(amber=(255, 204, 51), green=(61, 220, 132), cyan=(76, 201, 240),
           pink=(255, 92, 138), violet=(167, 139, 250))
INK, WHITE = (14, 16, 32), (238, 240, 255)

def dk(c, f=.72): return tuple(int(v * f) for v in c)

class P:
    def __init__(s):
        s.im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def r(s, x0, y0, x1, y1, c): s.d.rectangle([x0, y0, x1, y1], fill=c)
    def e(s, x0, y0, x1, y1, c): s.d.ellipse([x0, y0, x1, y1], fill=c)
    def px(s, pts, c):
        for x, y in pts: s.d.point((x, y), fill=c)
    def line(s, pts, c, w=1): s.d.line(pts, fill=c, width=w)

def corpo(p, roupa, pele):
    # ombros + pescoco: base comum do enquadramento (busto de frente)
    p.e(7, 34, 40, 60, roupa); p.r(7, 44, 40, 47, roupa)
    p.r(9, 40, 11, 47, dk(roupa)); p.r(36, 40, 38, 47, dk(roupa))
    p.r(21, 29, 26, 35, dk(pele, .85))

def cabeca(p, pele, olhos=INK, boca=None):
    p.e(15, 10, 32, 31, pele)
    p.r(30, 16, 31, 26, dk(pele, .88))          # sombra lateral
    p.r(14, 19, 15, 23, pele); p.r(32, 19, 33, 23, dk(pele, .88))  # orelhas
    p.r(19, 19, 20, 21, olhos); p.r(27, 19, 28, 21, olhos)
    p.px([(19, 19), (27, 19)], WHITE)
    p.r(17, 24, 18, 24, dk(pele, .9)); p.r(29, 24, 30, 24, dk(pele, .9))  # bochecha
    p.line([(22, 26), (25, 26)], boca or dk(pele, .55))
    p.px([(21, 25), (26, 25)], boca or dk(pele, .55))

def claudio(p):  # PM: prancheta, lapis na orelha, gravata
    pele, roupa, cab = (226, 172, 128), (60, 66, 110), (70, 45, 30)
    corpo(p, roupa, pele)
    p.r(20, 35, 27, 38, WHITE); p.r(23, 36, 24, 46, PAL["amber"])  # colarinho e gravata
    cabeca(p, pele)
    p.e(15, 8, 32, 18, cab); p.r(15, 12, 16, 19, cab); p.r(31, 12, 32, 19, cab)
    p.r(18, 13, 29, 15, cab)                                     # franja reta
    for x0 in (17, 25):                                          # oculos
        p.r(x0 + 1, 19, x0 + 3, 21, (200, 225, 245)); p.r(x0 + 2, 19, x0 + 2, 21, INK)
        p.r(x0, 18, x0 + 4, 18, INK); p.r(x0, 22, x0 + 4, 22, INK)
        p.r(x0, 18, x0, 22, INK); p.r(x0 + 4, 18, x0 + 4, 22, INK)
    p.r(22, 19, 24, 19, INK)
    p.line([(33, 15), (37, 8)], PAL["amber"], 2); p.px([(37, 7), (38, 7)], (240, 150, 150))  # lapis
    p.r(26, 33, 41, 47, (150, 100, 55)); p.r(28, 35, 39, 47, WHITE)   # prancheta
    p.r(31, 32, 36, 35, (190, 195, 210)); p.r(32, 31, 35, 32, (150, 155, 170))
    for y in (38, 41, 44):
        p.r(30, y, 31, y + 1, PAL["green"]); p.r(33, y, 38, y, (150, 155, 180))

def valdir(p):  # Dev: fone grande, moletom com capuz caido, notebook </>
    pele, roupa, cab = (141, 94, 62), dk(PAL["green"], .55), (25, 20, 18)
    corpo(p, roupa, pele)
    p.e(11, 30, 36, 40, dk(roupa, .8))                          # capuz caido
    p.r(22, 36, 22, 44, WHITE); p.r(25, 36, 25, 43, WHITE)       # cordoes
    cabeca(p, pele)
    p.e(15, 7, 32, 17, cab); p.px([(18, 7), (22, 6), (26, 6), (29, 7)], cab)
    p.r(15, 11, 16, 17, cab); p.r(31, 11, 32, 17, cab)
    p.line([(13, 17), (16, 7), (31, 7), (34, 17)], (60, 64, 90), 2)  # arco do fone
    p.r(10, 16, 15, 25, (60, 64, 90)); p.r(32, 16, 37, 25, (60, 64, 90))
    p.r(11, 18, 13, 23, PAL["green"]); p.r(34, 18, 36, 23, PAL["green"])
    p.r(8, 38, 39, 47, (90, 96, 130)); p.r(10, 39, 37, 47, (35, 40, 70))  # notebook
    p.px([(20, 42), (19, 43), (20, 44), (27, 42), (28, 43), (27, 44)], PAL["green"])
    p.line([(25, 41), (22, 45)], PAL["green"])

def samara(p):  # QA: coque alto, lupa grande, checklist
    pele, roupa, cab = (247, 205, 170), dk(PAL["cyan"], .55), (180, 70, 40)
    corpo(p, roupa, pele)
    p.r(14, 37, 21, 47, WHITE)                                   # checklist
    for y in (39, 42, 45):
        p.px([(15, y), (16, y + 1), (17, y)], PAL["green"]); p.r(18, y, 20, y, (150, 155, 180))
    cabeca(p, pele)
    p.e(14, 8, 33, 19, cab); p.r(14, 12, 16, 24, cab); p.r(31, 12, 33, 24, cab)
    p.e(19, 1, 28, 9, cab); p.r(20, 8, 27, 9, PAL["cyan"])      # coque + elastico
    p.r(17, 13, 24, 14, cab)                                     # franja lateral
    p.line([(33, 33), (37, 40)], (120, 80, 50), 3)               # cabo da lupa
    p.e(24, 15, 41, 32, (200, 205, 220)); p.e(26, 17, 39, 30, (170, 230, 250))
    p.r(29, 20, 31, 21, WHITE); p.r(29, 22, 29, 23, WHITE)
    p.r(33, 22, 34, 24, INK)                                     # olho ampliado

def antonio(p):  # Videos: bone virado, claquete
    pele, roupa, cab = (196, 134, 90), dk(PAL["pink"], .5), (40, 28, 22)
    corpo(p, roupa, pele)
    cabeca(p, pele)
    p.r(15, 15, 16, 20, cab); p.r(31, 15, 32, 20, cab)
    p.e(14, 7, 33, 19, PAL["pink"]); p.r(14, 14, 33, 15, dk(PAL["pink"]))  # bone
    p.r(21, 6, 26, 7, dk(PAL["pink"])); p.r(23, 5, 24, 5, WHITE)
    p.r(12, 15, 35, 17, dk(PAL["pink"]))                          # aba
    # claquete erguida a esquerda
    p.r(2, 31, 17, 45, INK); p.r(4, 34, 15, 44, (50, 52, 75))
    p.line([(4, 38), (14, 38)], WHITE); p.line([(4, 41), (11, 41)], WHITE)
    p.r(1, 25, 18, 29, WHITE)
    for x in (2, 7, 12, 17): p.line([(x, 29), (x + 3, 25)], INK, 2)
    p.r(16, 40, 19, 44, pele)                                    # mao

def josefa(p):  # Marketing: cabelo black power, megafone, balao com coracao
    pele, roupa, cab = (110, 70, 45), dk(PAL["violet"], .55), (30, 20, 22)
    corpo(p, roupa, pele)
    p.e(8, 2, 39, 30, cab)                                       # volume do cabelo
    for x, y in ((8, 10), (37, 11), (11, 4), (34, 4), (22, 1), (7, 20), (39, 21)):
        p.e(x - 2, y - 2, x + 2, y + 2, cab)
    cabeca(p, pele, boca=WHITE)
    p.r(22, 25, 25, 27, (120, 20, 40)); p.r(22, 25, 25, 25, WHITE)  # boca aberta
    p.px([(18, 17), (19, 16), (20, 16), (27, 16), (28, 16), (29, 17)], cab)
    p.r(16, 22, 16, 25, PAL["amber"]); p.r(31, 22, 31, 25, PAL["amber"])  # brincos
    # megafone apontando para fora (direita)
    p.d.polygon([(27, 37), (45, 27), (45, 47), (27, 43)], fill=WHITE)
    p.d.polygon([(29, 38), (44, 30), (44, 32), (29, 39)], fill=(200, 205, 220))
    p.r(44, 27, 46, 47, PAL["violet"]); p.r(24, 37, 29, 43, (90, 96, 130))
    p.r(25, 43, 27, 47, (60, 64, 90))
    for x, y in ((40, 23), (43, 21), (46, 19)): p.px([(x, y)], PAL["amber"])  # ondas de som

def basilio(p):  # Arte: boina, bigode, pincel e paleta
    pele, roupa, cab = (232, 184, 140), (230, 120, 60), (90, 60, 40)
    corpo(p, roupa, pele)
    p.r(18, 34, 29, 47, (245, 240, 225)); p.r(17, 34, 30, 35, (245, 240, 225))  # avental
    p.px([(20, 40), (21, 41), (26, 43), (27, 38)], PAL["violet"]); p.px([(24, 45)], PAL["cyan"])
    cabeca(p, pele)
    p.r(15, 15, 16, 21, cab); p.r(31, 15, 32, 21, cab)
    p.e(8, 7, 34, 15, (200, 40, 50)); p.e(6, 10, 14, 16, (200, 40, 50))  # boina larga caida
    p.r(15, 13, 32, 14, dk((200, 40, 50))); p.r(23, 5, 24, 7, (200, 40, 50))
    p.r(19, 24, 28, 25, cab); p.px([(18, 25), (29, 25)], cab)    # bigode
    # paleta (feijao) com tintas, embaixo a esquerda
    p.e(1, 33, 20, 47, (196, 150, 100)); p.e(12, 41, 16, 45, (0, 0, 0, 0))
    for (x, y), c in zip(((4, 37), (8, 35), (13, 36), (5, 42)),
                         (PAL["pink"], PAL["amber"], PAL["cyan"], PAL["green"])):
        p.r(x, y, x + 2, y + 2, c)
    # pincel erguido a direita
    p.line([(33, 44), (41, 22)], (150, 100, 55), 2)
    p.r(40, 20, 42, 22, (200, 200, 210)); p.r(41, 16, 43, 19, PAL["violet"])
    p.r(32, 40, 36, 45, pele)                                    # mao

def contorno(im):
    a, o = im.load(), im.copy(); b = o.load()
    for y in range(N):
        for x in range(N):
            if a[x, y][3]: continue
            if any(0 <= x + dx < N and 0 <= y + dy < N and a[x + dx, y + dy][3]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                b[x, y] = OUT + (255,)
    return o

def render(fn, acento):
    p = P(); fn(p)
    bg = Image.new("RGBA", (N, N), BG + (255,)); d = ImageDraw.Draw(bg)
    d.ellipse([4, 4, 43, 43], fill=tuple(int(b + (a - b) * .3) for a, b in zip(PAL[acento], BG)) + (255,))   # holofote atras
    d.rectangle([0, 44, 47, 47], fill=(23, 26, 51, 255))
    bg.alpha_composite(contorno(p.im))
    return bg.convert("RGB").resize((N * ESC, N * ESC), Image.NEAREST)

TIME = [("claudio", claudio, "amber"), ("valdir", valdir, "green"), ("samara", samara, "cyan"),
        ("antonio", antonio, "pink"), ("josefa", josefa, "violet"), ("basilio", basilio, "amber")]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    imgs = []
    for nome, fn, ac in TIME:
        im = render(fn, ac); im.save(f"{out}/{nome}.png"); imgs.append(im)
    folha = Image.new("RGB", (240 * 3 + 40, 240 * 2 + 30), (14, 16, 32))
    for i, im in enumerate(imgs): folha.paste(im, (10 + (i % 3) * 250, 10 + (i // 3) * 250))
    folha.save(f"{out}/_folha.png")
    # teste da silhueta
    sil = Image.new("RGB", (48 * 6 * 3, 48 * 3), WHITE)
    for i, (nome, fn, ac) in enumerate(TIME):
        p = P(); fn(p); m = p.im.split()[3].point(lambda v: 255 if v else 0)
        s = Image.new("RGB", (48, 48), WHITE); s.paste(INK, mask=m)
        sil.paste(s.resize((144, 144), Image.NEAREST), (i * 144, 0))
    sil.save(f"{out}/_silhuetas.png")
