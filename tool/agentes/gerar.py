"""Seis avatares manuais, sem IA. Fonte base local intocada; 48 px, escala visual 240.
Uso: uv run --with pillow --with numpy python tool/agentes/gerar.py
Candidatos e quadros vao para a Ponte; somente seis folhas PNG48 vao ao site.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import personas_base as base

ROOT=Path(__file__).resolve().parents[2]
DURATIONS=[240,180,180,240,180,240,240,180,120,120,240,300]
BLINKS={'claudio':(8,9),'valdir':(6,7),'samara':(9,10),'antonio':(7,8),'josefa':(5,6),'basilio':(8,9)}
SPECS={name:dict(fn=fn,accent=accent) for name,fn,accent in base.TIME}

class Recorder:
    def __init__(self):self.ops=[];self.d=self
    def r(self,*args):self.ops.append(('r',args,{}))
    def e(self,*args):self.ops.append(('e',args,{}))
    def px(self,*args):self.ops.append(('px',args,{}))
    def line(self,pts,c,w=1):self.ops.append(('line',(pts,c,w),{}))
    def polygon(self,*args,**kwargs):self.ops.append(('polygon',args,kwargs))

class AuditDraw:
    def __init__(self,owner,draw):self.owner,self.draw=owner,draw
    def __getattr__(self,name):
        def call(points,*args,**kwargs):
            if self.owner.audit:
                pairs=list(zip(points[::2],points[1::2])) if isinstance(points[0],(int,float)) else points
                assert all(0<=x<48 and 0<=y<48 for x,y in pairs),(name,points)
            return getattr(self.draw,name)(points,*args,**kwargs)
        return call
class P(base.P):
    def __init__(self):
        super().__init__();self.audit=False;self.d=AuditDraw(self,self.d)

def marker(ops,kind,coords):
    return next(i for i,(m,a,k) in enumerate(ops) if m==kind and a[:len(coords)]==coords)
def prepare():
    for name,spec in SPECS.items():
        recorder=Recorder();spec['fn'](recorder);ops=recorder.ops;spec['all']=ops
        if name=='samara':
            i=marker(ops,'r',(14,37,21,47));j=next(i for i,(m,a,k) in enumerate(ops) if m=='line' and a[0]==[(33,33),(37,40)])
            spec['checklist']=ops[i:i+7];spec['object']=ops[j:];spec['static']=ops[:i]+ops[i+7:j]
        else:
            markers={'claudio':('r',(26,33,41,47)),'valdir':('r',(8,38,39,47)),
                     'antonio':('r',(2,31,17,45)),'basilio':('e',(1,33,20,47))}
            i=next(i for i,(m,a,k) in enumerate(ops) if m=='polygon') if name=='josefa' else marker(ops,*markers[name])
            spec['static'],spec['object']=ops[:i],ops[i:]

def replay(p,ops,blink=False,stage=0,offset=(0,0)):
    dx,dy=offset
    for method,args,kwargs in ops:
        a=list(args)
        if blink:
            if method=='r' and tuple(a[:4]) in ((19,19,20,21),(27,19,28,21)):
                x=a[0];p.line([(x,20+stage),(x+1,20+stage)],base.INK);continue
            if method=='px' and a[0]==[(19,19),(27,19)] and a[1]==base.WHITE:continue
            if method=='r' and tuple(a[:4]) in ((19,19,19,21),(27,19,27,21)):
                x=a[0];p.r(x-1,20+stage,x+1,20+stage,base.INK);continue
        if method in ('r','e'):a[:4]=[a[0]+dx,a[1]+dy,a[2]+dx,a[3]+dy]
        elif method in ('line','px','polygon'):a[0]=[(x+dx,y+dy) for x,y in a[0]]
        if method=='polygon':p.d.polygon(*a,**kwargs)
        else:getattr(p,method)(*a,**kwargs)

def claudio(p,k,blink,stage):
    replay(p,SPECS['claudio']['object'])
    tips=[None,(35,40),(34,39),(35,39),(36,39),(34,42),(35,42),(36,42),(35,42),(34,40),(36,40),None]
    tip=tips[k]
    if tip:
        tx,ty=tip;hx,hy=tx+4,ty+3
        p.line([(43,47),(hx+1,hy+1)],(60,66,110),3)
        if k>=2:p.line([(33,39),(min(36,33+k),39)],base.INK)
        if k>=5:p.line([(33,42),(min(36,33+k-4),42)],base.INK)
        p.line([(tx,ty),(hx,hy)],base.PAL['amber'])
        p.px([(tx,ty)],base.INK)
        p.r(hx-1,hy,hx+1,min(47,hy+2),(226,172,128))

def valdir(p,k,blink,stage):
    ops=SPECS['valdir']['object'];replay(p,ops[:2])
    code=base.dk(base.PAL['green'],.55) if k in (3,4,8) else base.PAL['green']
    p.px([(20,42),(19,43),(20,44),(27,42),(28,43),(27,44)],code)
    p.line([(25,41),(22,45)],code)
    # Dedos emergem sobre a borda do teclado, alternando uma tecla por mao.
    skin=(141,94,62);arrival=1 if k in (1,10) else 0
    p.r(12,46+arrival,18,47,skin);p.r(29,46+arrival,35,47,skin)
    for x,pressed in ((14,k%2==0),(17,k%2!=0),(30,k%2!=0),(33,k%2==0)):
        top=44+arrival+(1 if pressed else 0);p.r(x,top,x+1,47,skin)
        p.px([(x,top)],base.dk(skin,.88))

def samara(p,k,blink,stage):
    checks=3 if k in (0,7,8,9,10,11) else (0 if k<3 else (1 if k<5 else 2))
    p.r(14,37,21,47,base.WHITE)
    for i,y in enumerate((39,42,45)):
        p.r(18,y,20,y,(150,155,180))
        if i<checks:p.px([(15,y),(16,y+1),(17,y)],base.PAL['green'])
    offsets=[(0,0),(-1,1),(-2,2),(-4,4),(-6,6),(-4,5),(-2,3),(0,1),(1,0),(0,0),(0,0),(0,0)]
    dx,dy=offsets[k]
    replay(p,SPECS['samara']['object'][:5],offset=(dx,dy))
    if dy>=3:
        p.line([(29+dx,23+dy),(31+dx,25+dy),(35+dx,21+dy)],base.PAL['green'],2)
    elif blink:p.r(32+dx,23+dy+stage,35+dx,23+dy+stage,base.INK)
    else:p.r(33+dx,22+dy,34+dx,24+dy,base.INK)
    if k not in (9,10):
        p.r(34+dx,37+dy,37+dx,40+dy,(247,205,170))

def antonio(p,k,blink,stage):
    ops=SPECS['antonio']['object'];replay(p,ops[:4])
    angle=[0,-4,-9,-16,-20,0,0,-10,-18,-8,0,0][k]*math.pi/180
    down=1 if k in (5,6,10) else 0
    def point(x,y):
        return (round(3+(x-3)*math.cos(angle)-(y-29)*math.sin(angle)),round(29+(x-3)*math.sin(angle)+(y-29)*math.cos(angle))+down)
    p.d.polygon([point(x,y) for x,y in ((1,25),(18,25),(18,29),(1,29))],fill=base.WHITE)
    for x in (2,7,12,17):p.line([point(x,29),point(x+3,25)],base.INK,2)
    p.r(2,29,4,31,base.INK);p.px([(3,30)],(190,195,210))
    replay(p,ops[-1:])

def josefa(p,k,blink,stage):
    ops=SPECS['josefa']['object'];dx=[0,-1,-3,-5,-5,-5,-4,-3,-2,-1,0,0][k];dy=[0,-1,-2,-3,-3,-3,-2,-2,-1,0,0,0][k]
    replay(p,ops[:-3],offset=(dx,dy))
    mouth=46+dx;cy=37+dy
    if dx<=-3:
        if k!=5:p.line([(mouth+2,cy-5),(mouth+3,cy-3),(mouth+3,cy+3),(mouth+2,cy+5)],base.PAL['amber'])
        if dx==-5 and k in (4,5):p.line([(mouth+4,cy-8),(mouth+5,cy-5),(mouth+6,cy),(mouth+5,cy+5),(mouth+4,cy+8)],base.PAL['amber'])
    else:replay(p,ops[-3:-1] if k==10 else ops[-3:])

def basilio(p,k,blink,stage):
    ops=SPECS['basilio']['object'];replay(p,ops[:6])
    tips=[(42,17),(42,20),(39,26),(31,30),(21,33),(12,36),(9,38),(13,36),(22,33),(32,28),(40,22),(42,17)]
    tx,ty=tips[k];hx,hy=34,43;dist=math.hypot(tx-hx,ty-hy);ux,uy=(tx-hx)/dist,(ty-hy)/dist
    def back(n):return (round(tx-ux*n),round(ty-uy*n))
    p.line([(hx,hy),back(4)],(150,100,55),2)
    p.line([back(5),back(3)],(200,200,210),3)
    p.line([back(2),(tx,ty)],base.PAL['violet'],3)
    if k in (5,6,7):
        p.px([(tx,ty),(max(2,tx-1),min(46,ty+1))],base.PAL['violet'])
        p.line([(10,38),(12,39)],base.PAL['violet'])
    replay(p,ops[-1:])

ACTIONS=dict(claudio=claudio,valdir=valdir,samara=samara,antonio=antonio,josefa=josefa,basilio=basilio)
def render(name,k,force_blink=None):
    spec=SPECS[name];p=P()
    blink=k in BLINKS[name] if force_blink is None else force_blink
    stage=BLINKS[name].index(k) if k in BLINKS[name] else 0
    if k in (0,11) and force_blink is None:replay(p,spec['all'])
    else:
        replay(p,spec['static'],blink,stage);p.audit=True;ACTIONS[name](p,k,blink,stage)
    bg=Image.new('RGBA',(48,48),base.BG+(255,));d=ImageDraw.Draw(bg)
    color=base.PAL[spec['accent']]
    d.ellipse([4,4,43,43],fill=tuple(int(b+(a-b)*.3) for a,b in zip(color,base.BG))+(255,))
    d.rectangle([0,44,47,47],fill=(23,26,51,255));bg.alpha_composite(base.contorno(p.im))
    result=bg.convert('RGB')
    if name=='samara':
        # A lupa revela uma sombra antes oculta; usar a sombra de pele ja visivel na paleta original.
        a=np.array(result);a[(a==[217,180,149]).all(2)]=[222,184,153];result=Image.fromarray(a)
    return result

def font(size):
    for name in ('Arial.ttf','DejaVuSans.ttf'):
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default()
def contact(all_frames,out):
    out.mkdir(parents=True,exist_ok=True);canvases=[]
    for k in range(12):
        canvas=Image.new('RGB',(760,580),base.INK);d=ImageDraw.Draw(canvas)
        d.text((12,10),'MAQUETE DOS AVATARES | 48 px em 5x, sem captura do site',font=font(17),fill=base.WHITE)
        for i,(name,fs) in enumerate(all_frames.items()):
            x=10+(i%3)*250;y=42+(i//3)*266
            canvas.paste(fs[k].resize((240,240),Image.Resampling.NEAREST),(x,y))
            d.text((x+8,y+242),name.capitalize(),font=font(16),fill=base.WHITE)
        canvases.append(canvas)
    canvases[0].save(out/'maquete-6-agentes.gif',save_all=True,append_images=canvases[1:],duration=DURATIONS,loop=0,optimize=False)
    for name,fs in all_frames.items():
        folder=out/'quadros'/name;folder.mkdir(parents=True,exist_ok=True)
        for i,im in enumerate(fs):im.resize((240,240),Image.Resampling.NEAREST).save(folder/f'{i:02d}.png')
    canvases[4].save(out/'maquete-contato.png')
    print(json.dumps(dict(primeira_previa=str(out/'maquete-6-agentes.gif'))),flush=True)

def sha(data):return hashlib.sha256(data).hexdigest()
def colors(im):return {c for count,c in im.getcolors(im.width*im.height)}
def palette_image(colors):
    pal=Image.new('P',(1,1));values=[v for c in colors for v in c];pal.putpalette(values+[0]*(768-len(values)));return pal
def indexed(im,pal):
    # Indices exatos evitam a aproximacao de cores do quantizador RGB do Pillow.
    table=pal.getpalette();lookup={table[i]<<16|table[i+1]<<8|table[i+2]:i//3 for i in range(0,768,3)}
    a=np.asarray(im,dtype=np.uint32);packed=a[:,:,0]<<16|a[:,:,1]<<8|a[:,:,2]
    unique,inverse=np.unique(packed,return_inverse=True)
    values=np.array([lookup[int(c)] for c in unique],dtype=np.uint8)[inverse].reshape(im.height,im.width)
    result=Image.frombytes('P',im.size,values.tobytes());result.putpalette(table)
    assert result.convert('RGB').tobytes()==im.tobytes();return result
def check_animation(path,expected,durations):
    with Image.open(path) as im:
        actual=[]
        for i in range(im.n_frames):
            im.seek(i);im.load();actual.append((im.convert('RGB').tobytes(),im.info['duration']))
    def merged(rows):
        result=[]
        for pixels,ms in rows:
            if result and result[-1][0]==pixels:result[-1]=(pixels,result[-1][1]+ms)
            else:result.append((pixels,ms))
        return result
    assert merged(actual)==merged([(f.tobytes(),ms) for f,ms in zip(expected,durations)]),(path,'pixels/tempos')
    return len(actual)
def shared_css():
    lines=[line for line in (ROOT/'site.css').read_text().splitlines()
           if line.startswith(('img[data-retrato-animado]', '.retrato-em-movimento{', '@keyframes retratos{'))]
    assert len(lines)==3,'CSS compartilhado da integracao deve existir'
    return '\n'.join(lines)

def benchmark(all_frames,out,reuse=False):
    folder=out/'formatos';folder.mkdir(parents=True,exist_ok=True)
    css=shared_css();(folder/'agentes-shared.css').write_text(css)
    bench={'duracoes_ms':DURATIONS,'loop_ms':sum(DURATIONS),'assets':{},'totais':{},
        'css_compartilhado':dict(arquivo='site.css',bytes=len(css.encode()),sha256=sha(css.encode()))}
    for name,fs in all_frames.items():
        palette_colors=sorted(set(c for im in fs for c in colors(im)));assert len(palette_colors)<=256
        pal=palette_image(palette_colors);rows={}
        for size in (48,240):
            scaled=[im if size==48 else im.resize((240,240),Image.Resampling.NEAREST) for im in fs]
            webp=folder/f'{name}-{size}.webp';gif=folder/f'{name}-{size}.gif';png=folder/f'{name}-sheet-{size}.png'
            if not reuse:
                indexed_frames=[indexed(im,pal) for im in scaled]
                indexed_frames[0].save(webp,save_all=True,append_images=indexed_frames[1:],duration=DURATIONS,loop=0,
                    lossless=True,quality=100,method=6,exact=True,minimize_size=True,allow_mixed=False)
                candidates=[]
                for optimize in (False,True):
                    candidate=folder/f'{name}-{size}-{int(optimize)}.gif'
                    indexed_frames[0].save(candidate,save_all=True,append_images=indexed_frames[1:],duration=DURATIONS,loop=0,optimize=optimize,disposal=2)
                    check_animation(candidate,scaled,DURATIONS);candidates.append((candidate.stat().st_size,candidate))
                _,best=min(candidates,key=lambda v:v[0]);shutil.copy2(best,gif)
                for _,candidate in candidates:candidate.unlink()
                sheet=Image.new('RGB',(size*12,size))
                for i,im in enumerate(scaled):sheet.paste(im,(i*size,0))
                indexed(sheet,pal).save(png)
                subprocess.run(['oxipng','-q','-o','4','--strip','safe',str(png)],check=True)
            for fmt,path in [('webp',webp),('gif',gif)]:
                count=check_animation(path,scaled,DURATIONS)
                rows[f'{fmt}{size}']=dict(bytes=path.stat().st_size,quadros_codificados=count,tamanho=[size,size])
            sheet=Image.open(png).convert('RGB');assert sheet.size==(size*12,size)
            for i,im in enumerate(scaled):assert sheet.crop((i*size,0,(i+1)*size,size)).tobytes()==im.tobytes(),(name,size,i,'recorte de folha')
            rows[f'png{size}']=dict(bytes=png.stat().st_size,tamanho=[size*12,size],recortes_exatos=True,rgba_decodificado_estimado=size*size*12*4)
        bench['assets'][name]=rows
    for fmt in ('webp48','gif48','webp240','gif240'):
        bench['totais'][fmt]=sum(row[fmt]['bytes'] for row in bench['assets'].values())
    for size in (48,240):
        total=sum(row[f'png{size}']['bytes'] for row in bench['assets'].values())
        bench['totais'][f'png_css{size}_compartilhado']=total+len(css.encode())
    bench['escolha']='png_css48_compartilhado'
    bench['criterio']='Seis folhas PNG48 + UM bloco CSS real compartilhado. IO/fallback/reduced sao comuns aos formatos; PNG usa apenas classe e keyframes CSS, sem player JS, timers ou DOM extra. Memoria e estimativa RGBA, nao medicao de navegador.'
    bench['economia_vs_webp48_bytes']=bench['totais']['webp48']-bench['totais'][bench['escolha']]
    bench['economia_vs_webp48_percentual']=round(100*bench['economia_vs_webp48_bytes']/bench['totais']['webp48'],3)
    dest=ROOT/'img/equipe/animados';dest.mkdir(parents=True,exist_ok=True)
    for name in all_frames:
        shutil.copy2(folder/f'{name}-sheet-48.png',dest/f'{name}.png')
        (dest/f'{name}.webp').unlink(missing_ok=True)
        saved=Image.open(dest/f'{name}.png').convert('RGB')
        for i,im in enumerate(all_frames[name]):assert saved.crop((i*48,0,(i+1)*48,48)).tobytes()==im.tobytes()
    for unused in folder.glob('*-sheet-*.css'):unused.unlink()
    (ROOT/'tool/agentes/benchformatos.json').write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n')
    (out/'benchformatos.json').write_text(json.dumps(bench,ensure_ascii=False,indent=2)+'\n')
    return bench

def validate(all_frames,out):
    assert set(all_frames)=={'claudio','valdir','samara','antonio','josefa','basilio'}
    original={name:base.render(spec['fn'],spec['accent']).resize((48,48),Image.Resampling.NEAREST) for name,spec in SPECS.items()}
    union=set(c for im in original.values() for c in colors(im));checks={}
    for name,fs in all_frames.items():
        assert len(fs)==12 and fs[0].tobytes()==original[name].tobytes()==fs[-1].tobytes()
        assert all(im.size==(48,48) and im.mode=='RGB' for im in fs)
        assert all(colors(im)<=union for im in fs),(name,'cor nova')
        assert len({im.tobytes() for im in fs})>=9,(name,'loop pouco distinto')
        for k in BLINKS[name]:
            a=np.array(render(name,k,False));b=np.array(render(name,k,True))
            assert np.any(a[8:32,14:35]!=b[8:32,14:35]),(name,k,'piscar deve alterar o rosto')
        for im in fs:
            big=np.array(im.resize((240,240),Image.Resampling.NEAREST))
            assert np.all(big==np.repeat(np.repeat(np.array(im),5,axis=0),5,axis=1))
        checks[name]=dict(quadros=12,poses_distintas=len({im.tobytes() for im in fs}),primeiro_igual_fonte=True,ultimo_igual_primeiro=True,
            blink_frames=BLINKS[name],frame_original_sha256=sha(original[name].tobytes()),paleta_original_sha256=sha(bytes(v for c in sorted(colors(original[name])) for v in c)))
    report=dict(ok=True,grade=[48,48],visual=[240,240],loop_ms=sum(DURATIONS),duracoes_ms=DURATIONS,
        fonte_base_sha256=sha((Path(__file__).parent/'personas_base.py').read_bytes()),paleta_uniao=sorted(union),
        paleta_uniao_sha256=sha(bytes(v for c in sorted(union) for v in c)),sem_novas_cores=True,sem_antialias=True,limites='Validacao de pixels e contratos; nao representa teste do site em navegador.',agentes=checks)
    return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',type=Path,default=Path.home()/'.fabrica/ponte/arquivos/site-agentes-animados');parser.add_argument('--reuse-encodings',action='store_true',help='Conferir e medir candidatos existentes sem recodificar');args=parser.parse_args()
    assert shutil.which('oxipng'),'oxipng precisa estar no PATH'
    originals={p:p.read_bytes() for p in (ROOT/'img/equipe').glob('*.webp')}
    prepare();all_frames={name:[render(name,k) for k in range(12)] for name in SPECS}
    contact(all_frames,args.artifacts)
    report=validate(all_frames,args.artifacts);bench=benchmark(all_frames,args.artifacts,args.reuse_encodings)
    assert all(p.read_bytes()==content for p,content in originals.items()),'fallback estatico deve ficar intocado'
    report['fallbacks_estaticos_preservados']=True
    report['fallbacks_sha256']={p.name:sha(content) for p,content in originals.items()}
    report['producao_png48_sha256']={name:sha((ROOT/f'img/equipe/animados/{name}.png').read_bytes()) for name in all_frames}
    for path in (ROOT/'tool/agentes/validacao.json',args.artifacts/'validacao.json'):
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(escolha=bench['escolha'],totais=bench['totais'])),flush=True)
if __name__=='__main__':main()
