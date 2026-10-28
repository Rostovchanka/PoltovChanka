"""Artist-release and time-period photographic transforms.

All source-derived. No inserted objects, painted masks, textures, or AI content.
No release selection applies a preset: parameters at zero are identity.
"""
import numpy as np
from scipy.ndimage import gaussian_filter
from album_catalog import COVERS, ALBUM_CONTROLS
from era_catalog import ERAS


def lum(a):
    return a[...,0]*.2126+a[...,1]*.7152+a[...,2]*.0722


def blur(a,r):
    if r<.01:return a
    return gaussian_filter(a,sigma=(max(.4,r),max(.4,r),0),mode='reflect')


def clip(a):
    return np.clip(a,0,1).astype(np.float32,copy=False)


def toward(a, color, q, mask=None):
    c=np.array(color,dtype=np.float32)
    if mask is not None:q=q*mask[...,None]
    return clip(a*(1-q)+c*q)


def process_caretaker(a,p,album_id='none'):
    if album_id not in COVERS:
        return a
    meta=COVERS[album_id]
    feature_keys=[f'cover_{album_id}_{i}' for i in range(5)]
    if not any(p.get(k,0)>0 for k,_,_ in ALBUM_CONTROLS) and not any(p.get(k,0)>0 for k in feature_keys):
        return a
    from engine import apply_album_covers
    a=apply_album_covers(a,p)
    palette=np.asarray(meta['palette'],dtype=np.float32)
    h,w=a.shape[:2]
    yy,xx=np.ogrid[-1:1:complex(h),-1:1:complex(w)]
    q=p.get(feature_keys[0],0)/100
    if q:
        l=lum(a)
        m=np.clip((l-.12)/.88,0,1)
        a=toward(a,palette,q*.23,m)
    q=p.get(feature_keys[1],0)/100
    if q:
        l=lum(a)
        hi=np.clip((l-.48)/.52,0,1)
        peak=np.clip(.75*palette+.25,0,1)
        a=toward(a,peak,q*.24,hi)
    q=p.get(feature_keys[2],0)/100
    if q:
        l=lum(a)
        mid=np.clip(1-np.abs(l-.48)/.48,0,1)
        neutral=l[...,None]
        saturated=toward(a,palette,.12)
        a=clip(a*(1-q*.23*mid[...,None])+saturated*(q*.23*mid[...,None]))
    q=p.get(feature_keys[3],0)/100
    if q:
        l=lum(a)
        shadow=np.clip((.58-l)/.58,0,1)
        a=clip(a*(1-shadow[...,None]*q*.18)+palette*shadow[...,None]*q*.045)
    q=p.get(feature_keys[4],0)/100
    if q:
        # Central subject/background separation is framing-aware, not object recognition.
        center=np.exp(-((xx/.65)**2+(yy/.74)**2))
        outer=(1-center)
        softened=blur(a,max(1,min(h,w)*.012))
        a=clip(a*(1-outer[...,None]*q*.23)+softened*(outer[...,None]*q*.23))
    return a


# Each era deliberately maps its named controls to corresponding image operations.
# Reuse occurs where two eras actually share a physical mechanism (e.g. a highlight
# shoulder), not merely to fill 15 slots with differently named generic sliders.
ERA_OPERATORS = {
    '1970s': [
        'warm_mid','warm_high','reduce_magenta','shadow_green','lift_toe',
        'roll_high','warm_halation','luma_grain','diffuse_high','warm_white',
        'orange_mask','reduce_green','cross_process','matte','distance_soft',
    ],
    '1980s': [
        'cyan_shadows','tungsten_mix','video_toe','roll_high','green_high',
        'blue_chroma','luma_bleed','chroma_shift','pink_white','flash_edge',
        'diffuse_high','cool_mid','densify_black','sat_cap','luma_echo',
    ],
    '1990s': [
        'beige_white','flash_core','green_white','magenta_shadows','blue_chroma',
        'roll_high','diffuse_edge','lift_toe','shadow_cool','flash_high',
        'compress_mid','corner_chroma','cool_high','densify_black','luma_echo',
    ],
    '2000s': [
        'cyan_high','flash_high','blue_shadows','cool_neutral','chroma_noise',
        'edge_sharp','mid_contrast','hard_clip','green_mid','magenta_shadows',
        'chroma_crosstalk','radial_flash','diffuse_edge','sat_cap','bright_flat',
    ],
    '2010s': [
        'hdr_lift','microcontrast','cool_white','blue_chroma','warm_high',
        'shadow_denoise','white_pop','matte','edge_sharp','shadow_desat',
        'cool_neutral','warm_target','tone_compress','bright_flat','fade',
    ],
}

def _color_tint(a,c,q,mask=None):
    c=np.asarray(c,dtype=np.float32)
    mask=1. if mask is None else mask[...,None]
    return clip(a+(c-.5)*q*mask)

def _operator(a,op,q,palette,era_index):
    if q<=0:return a
    h,w=a.shape[:2]
    l=lum(a)
    sh=np.clip((.58-l)/.58,0,1)
    hi=np.clip((l-.48)/.52,0,1)
    mid=np.clip(1-np.abs(l-.5)/.5,0,1)
    if op in ('warm_mid','warm_high','tungsten_mix','warm_target','orange_mask'):
        target={'warm_mid':(.85,.63,.35),'warm_high':(.94,.77,.51),
                'tungsten_mix':(.95,.67,.39),'warm_target':(.91,.73,.52),
                'orange_mask':(.93,.63,.33)}[op]
        m=mid if op in ('warm_mid','orange_mask') else hi
        if op=='tungsten_mix':m=np.clip(hi+.4*mid,0,1)
        return _color_tint(a,target,q*.19,m)
    if op in ('cool_mid','cyan_high','cyan_shadows','blue_shadows','cool_high','cool_white','cool_neutral','blue_chroma','shadow_cool'):
        c={'cool_mid':(.31,.63,.78),'cyan_high':(.38,.69,.85),
           'cyan_shadows':(.32,.57,.71),'blue_shadows':(.25,.44,.79),
           'cool_high':(.45,.68,.87),'cool_white':(.62,.74,.86),
           'cool_neutral':(.42,.67,.79),'blue_chroma':(.33,.46,.91),
           'shadow_cool':(.43,.49,.76)}[op]
        if op in ('cyan_shadows','blue_shadows','shadow_cool'):m=sh
        elif op in ('cyan_high','cool_high','cool_white'):m=hi
        elif op=='blue_chroma':
            m=np.clip(a[...,2]-a[...,0]+.10,0,1)
        else:m=mid
        return _color_tint(a,c,q*.20,m)
    if op in ('reduce_magenta','shadow_green','reduce_green','green_high','green_white','green_mid','magenta_shadows','pink_white'):
        if op=='reduce_magenta':
            a[...,0]=np.clip(a[...,0]-hi*q*.09,0,1)
            a[...,2]=np.clip(a[...,2]-hi*q*.04,0,1)
        elif op=='shadow_green': a[...,1]=np.clip(a[...,1]+sh*q*.06,0,1)
        elif op=='reduce_green': a[...,1]=np.clip(a[...,1]*(1-mid*q*.12),0,1)
        elif op=='green_high': a[...,1]=np.clip(a[...,1]+hi*q*.06,0,1)
        elif op=='green_white': a[...,1]=np.clip(a[...,1]+hi*q*.05,0,1)
        elif op=='green_mid': a[...,1]=np.clip(a[...,1]+mid*q*.06,0,1)
        elif op=='magenta_shadows':
            a[...,0]=np.clip(a[...,0]+sh*q*.08,0,1)
            a[...,1]=np.clip(a[...,1]-sh*q*.05,0,1)
        elif op=='pink_white':
            a[...,0]=np.clip(a[...,0]+hi*q*.05,0,1)
            a[...,1]=np.clip(a[...,1]-hi*q*.02,0,1)
        return a
    if op in ('lift_toe','video_toe','hdr_lift','matte'):
        strength={'lift_toe':.07,'video_toe':.04,'hdr_lift':.15,'matte':.11}[op]
        return clip(a+sh[...,None]*q*strength)
    if op in ('roll_high','flash_high','hard_clip','white_pop','tone_compress','flash_core'):
        if op=='white_pop':return clip(a+hi[...,None]*q*.10)
        if op=='flash_core':
            b=blur(a,max(1,min(h,w)*.01))
            return clip(a+(a-b)*hi[...,None]*q*.22)
        if op=='flash_high':return clip(a+hi[...,None]*q*.08-hi[...,None]**2*q*.12)
        if op=='hard_clip':return clip(a+hi[...,None]*q*.10)
        if op=='tone_compress':return clip(a+sh[...,None]*q*.07-hi[...,None]*q*.08)
        return clip(a-hi[...,None]*q*.12)
    if op=='warm_halation':
        b=blur(a,max(1,min(h,w)*.012))
        out=a.copy()
        out[...,0]=np.clip(out[...,0]+b[...,0]*hi*q*.19,0,1)
        out[...,1]=np.clip(out[...,1]+b[...,1]*hi*q*.08,0,1)
        return out
    if op=='luma_grain':
        rng=np.random.default_rng(1970)
        noise=rng.normal(0,q*.010,(h,w,1)).astype(np.float32)
        return clip(a+noise*mid[...,None])
    if op=='chroma_noise':
        rng=np.random.default_rng(2004)
        noise=rng.normal(0,q*.007,(h,w,3)).astype(np.float32)
        noise[...,1]*=.5
        return clip(a+noise*sh[...,None])
    if op in ('diffuse_high','diffuse_edge','distance_soft','bright_flat','shadow_denoise'):
        radius=max(.5,min(h,w)*(.004 if op=='diffuse_high' else .009))
        b=blur(a,radius)
        if op=='diffuse_high':m=hi
        elif op=='bright_flat':m=hi
        elif op=='shadow_denoise':m=sh
        elif op=='distance_soft':
            yy,xx=np.ogrid[-1:1:complex(h),-1:1:complex(w)]
            m=np.clip(np.abs(xx)*.55+np.abs(yy)*.45,0,1)
        else:
            yy,xx=np.ogrid[-1:1:complex(h),-1:1:complex(w)]
            m=np.clip((np.abs(xx)+np.abs(yy))/2,0,1)
        return clip(a*(1-q*.24*m[...,None])+b*(q*.24*m[...,None]))
    if op in ('warm_white','beige_white'):
        target=(.94,.86,.71) if op=='warm_white' else (.84,.76,.64)
        return toward(a,target,q*.18,hi)
    if op=='cross_process':return clip(a+(np.asarray(palette,dtype=np.float32)-.5)*(hi[...,None]-sh[...,None])*q*.15)
    if op in ('luma_bleed','luma_echo','chroma_shift','chroma_crosstalk'):
        if op=='chroma_crosstalk':
            result=a.copy()
            result[...,0]=a[...,0]*(1-q*.06)+a[...,1]*q*.06
            result[...,2]=a[...,2]*(1-q*.06)+a[...,1]*q*.06
            return clip(result)
        shifted=np.roll(a,max(1,int(w*(.002 if op=='chroma_shift' else .006))),axis=1)
        if op=='chroma_shift':
            result=a.copy();result[...,2]=a[...,2]*(1-q*.12)+shifted[...,2]*q*.12
            return clip(result)
        if op=='luma_bleed':
            b=blur(a,max(.8,min(h,w)*.007))
            return clip(a*(1-q*.13)+b*q*.13)
        return clip(a*(1-q*.08)+shifted*q*.08)
    if op in ('flash_edge','edge_sharp','microcontrast','mid_contrast'):
        b=blur(a,max(.8,min(h,w)*(.008 if op=='microcontrast' else .004)))
        amount={'flash_edge':.13,'edge_sharp':.25,'microcontrast':.24,'mid_contrast':.17}[op]
        mask=hi if op=='flash_edge' else mid if op=='mid_contrast' else np.ones_like(l)
        return clip(a+(a-b)*q*amount*mask[...,None])
    if op=='densify_black':return clip(a-sh[...,None]*q*.08)
    if op=='sat_cap':
        gray=l[...,None]
        chrom=a-gray
        strength=np.maximum(np.abs(chrom).max(axis=2),0)
        m=np.clip(strength*2.2,0,1)
        return clip(a-q*.24*m[...,None]*chrom)
    if op=='compress_mid':return clip(a+(.5-l)[...,None]*mid[...,None]*q*.09)
    if op=='corner_chroma':
        yy,xx=np.ogrid[-1:1:complex(h),-1:1:complex(w)]
        m=np.clip((np.abs(xx)+np.abs(yy))*.5,0,1)
        return clip(a*(1-q*.12*m[...,None])+l[...,None]*q*.12*m[...,None])
    if op=='radial_flash':
        yy,xx=np.ogrid[-1:1:complex(h),-1:1:complex(w)]
        rad=np.exp(-(xx**2/.45+yy**2/.40))
        return clip(a+rad[...,None]*hi[...,None]*q*.10)
    if op=='shadow_desat':
        return clip(a*(1-sh[...,None]*q*.28)+l[...,None]*sh[...,None]*q*.28)
    if op=='fade':
        return clip(a*(1-q*.14)+.06*q)
    return a


def process_era(a,p,era_id='none'):
    if era_id not in ERAS:return a
    meta=ERAS[era_id]
    entries=meta['controls']
    keys=[key for key,_,_ in entries]
    if not any(p.get(k,0)>0 for k in keys):return a
    ops=ERA_OPERATORS[era_id]
    palette=meta['palette']
    for (key,_,_),op in zip(entries,ops):
        strength=p.get(key,0)/100.0
        if strength:a=_operator(a,op,strength,palette,list(ERAS).index(era_id))
    return a
