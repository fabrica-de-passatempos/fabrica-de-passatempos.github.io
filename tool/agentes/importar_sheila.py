"""Converte o avatar aprovado da Sheila sem redesenhar pixels ou mudar tempos.
Uso: python3 tool/agentes/importar_sheila.py (Pillow).
"""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageSequence

ROOT=Path(__file__).resolve().parents[2]
INS=Path(__file__).resolve().parent/'insumos/sheila'

def main():
    origin=json.loads((INS/'origem.json').read_text())
    for name,sha in origin['hashes_aprovados'].items():
        assert hashlib.sha256((INS/name).read_bytes()).hexdigest()==sha
    frames=[];durations=[];originals=[]
    for f in ImageSequence.Iterator(Image.open(INS/'sheila.webp')):
        f.load();original=f.convert('RGB').copy();small=original.resize((48,48),Image.Resampling.NEAREST)
        assert small.resize((240,240),Image.Resampling.NEAREST).tobytes()==original.tobytes()
        frames.append(small);originals.append(original);durations.append(f.info['duration'])
    assert len(frames)==7 and sum(durations)==2800
    assert frames[0].tobytes()==frames[-1].tobytes()
    palette={tuple(c)for c in json.loads((ROOT/'tool/agentes/validacao.json').read_text())['paleta_uniao']}
    colors={c for f in frames for c in f.getdata()};assert colors<=palette
    target=ROOT/'img/equipe/animados/sheila.webp';target.parent.mkdir(parents=True,exist_ok=True)
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=durations,loop=0,
                   lossless=True,quality=100,method=6,minimize_size=True,allow_mixed=False)
    decoded=Image.open(target);assert decoded.info['loop']==0 and decoded.n_frames==7
    for i,f in enumerate(ImageSequence.Iterator(decoded)):
        f.load();assert f.info['duration']==durations[i]
        assert f.convert('RGB').resize((240,240),Image.Resampling.NEAREST).tobytes()==originals[i].tobytes()
    static=ROOT/'img/equipe/sheila.webp';shutil.copy2(INS/'sheila-estatica.webp',static)
    assert Image.open(static).convert('RGB').tobytes()==originals[0].tobytes()
    report={'autoria':'Sheila','pixels_e_tempos_aprovados_preservados':True,'sem_redesenho':True,
            'grade':[48,48],'tamanho_html':[240,240],'quadros_codificados':7,'duracoes_ms':durations,'ciclo_ms':2800,'cores':len(colors),'paleta_existente':True,
            'bytes_animacao':target.stat().st_size,'bytes_original_aprovado':(INS/'sheila.webp').stat().st_size,
            'bytes_estatico':static.stat().st_size,'sha256_animacao':hashlib.sha256(target.read_bytes()).hexdigest(),
            'sha256_estatico':hashlib.sha256(static.read_bytes()).hexdigest(),'aprovacao':origin['aprovacao']}
    (ROOT/'tool/agentes/sheila.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
