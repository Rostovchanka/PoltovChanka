"""Elsewhere Studio image engine.

Shared photo-development controls apply to RAW, JPEG, PNG, and TIFF.
RAW-only differences are limited to decode-time options handled outside this file.
The distinctive workspaces are photographic transforms designed for liminal editing,
not stock textures or generative scene content.
"""
from __future__ import annotations
import math
import numpy as np
from scipy.ndimage import gaussian_filter, affine_transform
from scipy.interpolate import PchipInterpolator

RAW_EXTENSIONS = {'.cr3','.cr2','.dng','.nef','.arw','.raf','.orf','.rw2','.pef','.srw'}
DEFAULT_GEOMETRY = dict(move_x=0.0,move_y=0.0,zoom=100.0,rotation=0.0)

# --- UI/workspace definitions -------------------------------------------------
GROUPS = {
    'Develop': [
        ('exposure','Exposure · EV',-4,4,.05),('contrast','Contrast',-100,100,1),
        ('highlights','Highlights',-100,100,1),('shadows','Shadows',-100,100,1),
        ('whites','Whites',-100,100,1),('blacks','Blacks',-100,100,1),
        ('clarity','Clarity',-100,100,1),('dehaze','Dehaze',-100,100,1),
        ('sharpen','Sharpen',0,100,1),('denoise','Noise reduction',0,100,1),
    ],
    'Color': [
        ('temperature','Warmth',-100,100,1),('tint','Green ↔ magenta',-100,100,1),
        ('saturation','Saturation',-100,100,1),('vibrance','Vibrance',-100,100,1),
    ],
    'Curves': [
        ('curve_0','Black anchor',0,100,1),('curve_25','Quarter-tones',0,100,1),
        ('curve_50','Midtones',0,100,1),('curve_75','Upper-mids',0,100,1),
        ('curve_100','White anchor',0,100,1),
    ],
    'Color Wheels': [
        ('shadow_hue','Shadows hue',0,360,1),('shadow_strength','Shadows amount',0,100,1),
        ('mid_hue','Midtones hue',0,360,1),('mid_strength','Midtones amount',0,100,1),
        ('highlight_hue','Highlights hue',0,360,1),('highlight_strength','Highlights amount',0,100,1),
    ],
    'Backrooms · Level 0': [
        ('l0_yellow_bias','Yellow fluorescence',0,100,1),('l0_ballast_green','Ballast green drift',0,100,1),
        ('l0_ceiling_rolloff','Ceiling rolloff',0,100,1),('l0_corner_nicotine','Corner nicotine stain',0,100,1),
        ('l0_wall_flatten','Wall flatness',0,100,1),('l0_carpet_sink','Carpet sink',0,100,1),
        ('l0_drywall_drift','Drywall drift',0,100,1),('l0_fixture_bloom','Fixture bloom',0,100,1),
        ('l0_memory_bleach','Memory bleach',0,100,1),('l0_corridor_hum','Corridor hum',0,100,1),
    ],
    'Backrooms · Level 1': [
        ('l1_concrete_blanch','Concrete blanch',0,100,1),('l1_mercury_cyan','Mercury cyan',0,100,1),
        ('l1_sodium_residue','Sodium residue',0,100,1),('l1_strip_flicker','Striplight flicker',0,100,1),
        ('l1_floor_sheen','Floor sheen',0,100,1),('l1_ramp_falloff','Ramp falloff',0,100,1),
        ('l1_security_bleach','Security bleach',0,100,1),('l1_shadow_blue','Shadow blueing',0,100,1),
        ('l1_damp_stain','Damp stain',0,100,1),('l1_reverb','Concrete reverb',0,100,1),
    ],
    'Backrooms · Level 4': [
        ('l4_fluor_flatness','Fluorescent flatness',0,100,1),('l4_beige_drain','Beige drain',0,100,1),
        ('l4_copy_paper','Copy-paper whites',0,100,1),('l4_drop_ceiling','Drop-ceiling pressure',0,100,1),
        ('l4_dead_air','Dead-air washout',0,100,1),('l4_cube_silence','Cubicle silence',0,100,1),
        ('l4_monitor_cool','Monitor coolness',0,100,1),('l4_file_blue','File-cabinet blue',0,100,1),
        ('l4_linoleum_sheen','Linoleum sheen',0,100,1),('l4_after_hours','After-hours suspension',0,100,1),
    ],
    'Backrooms · Level 5': [
        ('l5_velvet_amber','Velvet amber',0,100,1),('l5_lacquer_red','Lacquer red-brown',0,100,1),
        ('l5_chandelier_halation','Chandelier halation',0,100,1),('l5_wallpaper_mute','Wallpaper mute',0,100,1),
        ('l5_corridor_depth','Corridor depth crush',0,100,1),('l5_bar_smoke','Bar-smoke veil',0,100,1),
        ('l5_carpet_crush','Carpet crush',0,100,1),('l5_mirror_smear','Mirror smear',0,100,1),
        ('l5_ballroom_gold','Ballroom gold',0,100,1),('l5_haunted_glow','Haunted glow',0,100,1),
    ],
    'Album Covers · The Caretaker': [
        ('ac_varnish_amber','Varnish amber',0,100,1),('ac_patina_olive','Patina olive',0,100,1),
        ('ac_canvas_flatten','Canvas flattening',0,100,1),('ac_pigment_fade','Pigment fade',0,100,1),
        ('ac_repro_blur','Reproduction blur',0,100,1),('ac_gallery_shadow','Gallery shadow',0,100,1),
        ('ac_frame_falloff','Frame falloff',0,100,1),('ac_detail_erosion','Detail erosion',0,100,1),
        ('ac_memory_smear','Memory smear',0,100,1),('ac_oil_darkening','Oil darkening',0,100,1),
        ('ac_clouded_highlights','Clouded highlights',0,100,1),('ac_sepia_dust','Sepia dust',0,100,1),
        ('ac_figure_obscurity','Figure obscurity',0,100,1),('ac_print_bleed','Print bleed',0,100,1),
        ('ac_quiet_space','Quiet-space isolation',0,100,1),
    ],
    'Institutional': [
        ('inst_white_tube','White-tube severity',0,100,1),('inst_ballast_roll','Ballast roll',0,100,1),
        ('inst_chalky_paint','Chalky paint',0,100,1),('inst_wax_floor','Wax-floor coldness',0,100,1),
        ('inst_exit_sign_bleed','Exit-sign bleed',0,100,1),('inst_beige_absorb','Beige absorption',0,100,1),
        ('inst_tile_coldness','Tile coldness',0,100,1),('inst_office_green','Office green cast',0,100,1),
        ('inst_hospital_blue','Hospital blue',0,100,1),('inst_ceiling_deadzone','Ceiling deadzone',0,100,1),
        ('inst_corner_pressure','Corner pressure',0,100,1),('inst_mercury_pulse','Mercury pulse',0,100,1),
        ('inst_cleaner_residue','Cleaner residue',0,100,1),('inst_drained_daylight','Drained daylight',0,100,1),
        ('inst_corridor_distance','Corridor distance',0,100,1),
    ],

}

WORKSPACE_TABS = {
    'Core': ['Develop','Color','Curves','Color Wheels'],
    'Backrooms': ['Backrooms · Level 0','Backrooms · Level 1','Backrooms · Level 4','Backrooms · Level 5'],
    'Album Covers': ['Album Covers · The Caretaker'],
    'Institutional': ['Institutional'],
    'Temporal': [],
}

PRESETS = {}  # left empty intentionally: workspaces are editable, not preset-driven.
BANDS = ()

DEFAULTS = {}
for section in GROUPS.values():
    for key,label,lo,hi,step in section:
        if key.startswith('curve_'):
            DEFAULTS[key] = float(key.split('_')[1])
        elif key.endswith('_hue') and key in ('shadow_hue','mid_hue','highlight_hue'):
            DEFAULTS[key] = {'shadow_hue':220.,'mid_hue':60.,'highlight_hue':42.}[key]
        else:
            DEFAULTS[key] = 0.0

# --- numeric helpers ----------------------------------------------------------
def normalized(rgb:np.ndarray)->np.ndarray:
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype not in (np.uint8, np.uint16):
        raise ValueError('Expected RGB uint8 or uint16 image')
    scale = 65535.0 if rgb.dtype == np.uint16 else 255.0
    return rgb.astype(np.float32) / scale

def to_linear(srgb):
    return np.where(srgb<=0.04045, srgb/12.92, ((np.maximum(srgb,0)+0.055)/1.055)**2.4)

def to_srgb(linear):
    linear=np.maximum(linear,0)
    return np.where(linear<=0.0031308, 12.92*linear, 1.055*np.power(linear, 1/2.4)-0.055)

def blur(a, radius):
    if radius <= 0.01: return a
    return gaussian_filter(a, sigma=(radius,radius,0), mode='reflect')

def curves_lut(p):
    anchors=[p[f'curve_{n}']/100.0 for n in (0,25,50,75,100)]
    xp=np.array([0,.25,.5,.75,1.],dtype=np.float32)
    curve=PchipInterpolator(xp, anchors)(np.linspace(0,1,4097))
    return np.clip(curve,0,1).astype(np.float32)

def apply_tone_curve(a,p):
    if all(abs(p[f'curve_{n}']-n)<1e-6 for n in (0,25,50,75,100)):
        return a
    lum=np.clip(.2126*a[...,0]+.7152*a[...,1]+.0722*a[...,2],0,1)
    lut=curves_lut(p)
    idx=lum*4096.0
    lo=np.floor(idx).astype(np.int16)
    hi=np.minimum(lo+1,4096)
    mapped=lut[lo]*(1-(idx-lo))+lut[hi]*(idx-lo)
    ratio=(mapped/np.maximum(lum,1e-5))[...,None]
    return np.where(lum[...,None]>1e-5, a*ratio, mapped[...,None]).astype(np.float32)

def geometry_transform(a,g):
    h,w=a.shape[:2]
    dx=float(g.get('move_x',0))/100.0*w; dy=float(g.get('move_y',0))/100.0*h
    scale=max(.05,float(g.get('zoom',100))/100.0); th=math.radians(float(g.get('rotation',0)))
    if abs(dx)+abs(dy)+abs(scale-1)+abs(th)<1e-8: return a
    c,s=math.cos(th), math.sin(th)
    mat=np.array([[c,s],[-s,c]],dtype=np.float64)/scale
    center=np.array([(h-1)/2,(w-1)/2]); offset=center-mat@(center+np.array([dy,dx]))
    return np.stack([
        affine_transform(a[:,:,k],mat,offset=offset,output_shape=(h,w),order=1,mode='constant',cval=0,prefilter=False)
        for k in range(3)
    ],axis=-1)

def rgb_to_hsv(a):
    import cv2
    return cv2.cvtColor(np.ascontiguousarray(np.clip(a,0,1),dtype=np.float32), cv2.COLOR_RGB2HSV)

def hsv_to_rgb(a):
    import cv2
    return cv2.cvtColor(np.ascontiguousarray(a,dtype=np.float32), cv2.COLOR_HSV2RGB)

def lowfreq_field(h,w,seed=0,sigma=50):
    rng=np.random.default_rng(seed)
    tiny=rng.normal(0,1,(max(4,h//24),max(4,w//24))).astype(np.float32)
    up=np.kron(tiny,np.ones((math.ceil(h/tiny.shape[0]),math.ceil(w/tiny.shape[1])),dtype=np.float32))[:h,:w]
    field=gaussian_filter(up,sigma=max(2.0, sigma/12.0),mode='reflect')
    field-=field.min(); field/=max(float(np.ptp(field)),1e-6)
    return field

def soft_luma(a):
    return .2126*a[...,0]+.7152*a[...,1]+.0722*a[...,2]

def add_tint(a, rgb, amount, mask=None):
    if amount == 0: return a
    color=np.array(rgb,dtype=np.float32)
    m=1.0 if mask is None else mask[...,None]
    return np.clip(a + (color-0.5)*amount*m, 0, 1)

def scale_color(a, rgb_scale, amount, mask=None):
    if amount == 0: return a
    scale=np.array(rgb_scale,dtype=np.float32)
    m=1.0 if mask is None else mask[...,None]
    return np.clip(a*(1-m*amount) + a*scale*(m*amount),0,1)

def desaturate_except_hues(a, keep_center=55, keep_width=45, strength=.4):
    hsv=rgb_to_hsv(a)
    d=np.abs((hsv[...,0]-keep_center+180)%360-180)
    keep=np.clip(1-d/keep_width,0,1)
    hsv[...,1]*=(1-strength) + strength*keep
    return hsv_to_rgb(hsv)

# --- specialized workspace transforms ----------------------------------------
def apply_level0(a,p):
    if not any(v for k,v in p.items() if k.startswith("l0_")): return a
    h,w=a.shape[:2]; yy,xx=np.ogrid[-1:1:complex(h), -1:1:complex(w)]
    lum=soft_luma(a)
    field=lowfreq_field(h,w,11,60)
    # 1
    q=p['l0_yellow_bias']/100.0
    if q: a=scale_color(a,[1.12,1.10,0.88],q*0.75,mask=np.clip((lum-.18)/.82,0,1))
    # 2
    q=p['l0_ballast_green']/100.0
    if q:
        band=(np.sin(np.linspace(0,2*np.pi*9,h,dtype=np.float32))[:,None]+1)/2
        band=(band*0.5+0.5*field)
        a[...,1]=np.clip(a[...,1]+q*0.08*band,0,1)
        a[...,0]=np.clip(a[...,0]-q*0.025*band,0,1)
    # 3
    q=p['l0_ceiling_rolloff']/100.0
    if q:
        top=np.clip(1-((yy+1)/2),0,1)
        a=np.clip(a*(1-q*0.08) + a*(1+top[...,None]*q*0.16),0,1)
    # 4
    q=p['l0_corner_nicotine']/100.0
    if q:
        r=np.sqrt((xx*0.95)**2+(yy*1.05)**2)
        stain=np.clip((r-.18)/.9,0,1)**1.8
        a=add_tint(a,[0.82,0.72,0.32],q*0.35,mask=stain)
    # 5
    q=p['l0_wall_flatten']/100.0
    if q:
        m=np.clip(1-np.abs(lum-.66)/.32,0,1)
        b=blur(a, max(2,min(h,w)*.014))
        a=np.clip(a*(1-q*.35*m[...,None])+b*(q*.35*m[...,None]),0,1)
    # 6
    q=p['l0_carpet_sink']/100.0
    if q:
        floor=np.clip((yy+0.10)/1.10,0,1)
        a=scale_color(a,[0.88,0.83,0.70],q*0.40,mask=floor)
        a*=1-floor[...,None]*q*0.18
    # 7
    q=p['l0_drywall_drift']/100.0
    if q:
        drift=(field-0.5)
        a[...,0]=np.clip(a[...,0]+drift*q*0.10,0,1)
        a[...,1]=np.clip(a[...,1]+drift*q*0.08,0,1)
        a[...,2]=np.clip(a[...,2]-drift*q*0.05,0,1)
    # 8
    q=p['l0_fixture_bloom']/100.0
    if q:
        br=np.clip((lum-.56)*2.2,0,1)[...,None]
        a=np.clip(a+blur(a,[max(2,min(h,w)*.012)][0])*br*q*0.16,0,1)
        a=add_tint(a,[0.80,0.88,0.45],q*0.10,mask=br[...,0])
    # 9
    q=p['l0_memory_bleach']/100.0
    if q: a=desaturate_except_hues(a,55,40,q*0.72)
    # 10
    q=p['l0_corridor_hum']/100.0
    if q:
        rows=np.sin(np.linspace(0,2*np.pi*4,h,dtype=np.float32))[:,None]
        a=np.clip(a*(1+rows[...,None]*q*0.03),0,1)
    return a

def apply_level1(a,p):
    if not any(v for k,v in p.items() if k.startswith("l1_")): return a
    h,w=a.shape[:2]; yy,xx=np.ogrid[-1:1:complex(h), -1:1:complex(w)]
    lum=soft_luma(a); field=lowfreq_field(h,w,21,55)
    q=p['l1_concrete_blanch']/100.0
    if q:
        gray=lum[...,None]
        a=np.clip(a*(1-q*0.45)+gray*(q*0.45),0,1)
        a=scale_color(a,[0.95,0.97,1.0],q*0.25)
    q=p['l1_mercury_cyan']/100.0
    if q: a=add_tint(a,[0.40,0.62,0.78],q*0.28,mask=np.clip((lum-.25)/.75,0,1))
    q=p['l1_sodium_residue']/100.0
    if q: a=add_tint(a,[0.92,0.66,0.33],q*0.18,mask=np.clip((lum-.52)/.48,0,1))
    q=p['l1_strip_flicker']/100.0
    if q:
        bands=(np.sin(np.linspace(0,2*np.pi*12,h,dtype=np.float32))[:,None]*0.5+0.5)
        a=np.clip(a*(1+bands[...,None]*q*0.06-q*0.03),0,1)
    q=p['l1_floor_sheen']/100.0
    if q:
        floor=np.clip((yy+0.15)/1.15,0,1)*np.clip((lum-.18)/.82,0,1)
        a=add_tint(a,[0.55,0.66,0.74],q*0.18,mask=floor)
        a=np.clip(a + blur(a,max(2,min(h,w)*.008))*floor[...,None]*q*0.08,0,1)
    q=p['l1_ramp_falloff']/100.0
    if q:
        fall=np.clip((np.abs(xx)*0.55 + (yy+1)/2*0.45),0,1)
        a*=1-fall[...,None]*q*0.22
    q=p['l1_security_bleach']/100.0
    if q:
        hi=np.clip((lum-.60)/.40,0,1)
        a=np.clip(a*(1-hi[...,None]*q*0.18)+hi[...,None]*q*0.18,0,1)
    q=p['l1_shadow_blue']/100.0
    if q: a=add_tint(a,[0.38,0.46,0.82],q*0.26,mask=np.clip((.45-lum)/.45,0,1))
    q=p['l1_damp_stain']/100.0
    if q:
        damp=np.clip((field-.35)/.65,0,1)*np.clip((.7-lum)/.7,0,1)
        a=add_tint(a,[0.46,0.54,0.44],q*0.18,mask=damp)
    q=p['l1_reverb']/100.0
    if q:
        shifted=np.roll(a, max(1,int(w*(0.002+q*0.006))), axis=1)
        a=np.clip(a*(1-q*0.10)+shifted*(q*0.10),0,1)
    return a

def apply_level4(a,p):
    if not any(v for k,v in p.items() if k.startswith("l4_")): return a
    h,w=a.shape[:2]; yy,xx=np.ogrid[-1:1:complex(h), -1:1:complex(w)]
    lum=soft_luma(a); field=lowfreq_field(h,w,41,70)
    q=p['l4_fluor_flatness']/100.0
    if q:
        a=scale_color(a,[0.96,1.01,0.96],q*0.28)
        m=np.clip(1-np.abs(lum-.58)/.42,0,1)
        b=blur(a,max(2,min(h,w)*.01))
        a=np.clip(a*(1-q*0.28*m[...,None])+b*(q*0.28*m[...,None]),0,1)
    q=p['l4_beige_drain']/100.0
    if q:
        target=np.array([0.70,0.67,0.58],dtype=np.float32)
        a=np.clip(a*(1-q*0.22)+target*q*0.22,0,1)
    q=p['l4_copy_paper']/100.0
    if q: a=add_tint(a,[0.94,0.92,0.82],q*0.22,mask=np.clip((lum-.40)/.60,0,1))
    q=p['l4_drop_ceiling']/100.0
    if q:
        top=np.clip(1-((yy+1)/2),0,1)
        a*=1-top[...,None]*q*0.06
        a=scale_color(a,[1.0,1.02,0.98],q*0.12,mask=top)
    q=p['l4_dead_air']/100.0
    if q:
        a=np.clip(a*(1-q*0.10)+0.55*q*0.10,0,1)
    q=p['l4_cube_silence']/100.0
    if q:
        low=blur(a,max(2,min(h,w)*.018))
        a=np.clip(a*(1-q*0.18)+low*(q*0.18),0,1)
    q=p['l4_monitor_cool']/100.0
    if q:
        cool=np.clip((a[...,2]-a[...,0]+0.2),0,1)
        a=add_tint(a,[0.42,0.60,0.92],q*0.20,mask=cool)
    q=p['l4_file_blue']/100.0
    if q: a=add_tint(a,[0.44,0.53,0.72],q*0.22,mask=np.clip((.55-lum)/.55,0,1))
    q=p['l4_linoleum_sheen']/100.0
    if q:
        floor=np.clip((yy+0.12)/1.12,0,1)*np.clip((lum-.18)/.82,0,1)
        a=np.clip(a+blur(a,max(1,min(h,w)*.006))*floor[...,None]*q*0.10,0,1)
    q=p['l4_after_hours']/100.0
    if q:
        r=np.sqrt((xx*.85)**2+(yy*1.05)**2)
        edge=np.clip((r-.15)/.95,0,1)
        a*=1-edge[...,None]*q*0.16
        a=desaturate_except_hues(a,70,180,q*0.18)
    return a

def apply_level5(a,p):
    if not any(v for k,v in p.items() if k.startswith("l5_")): return a
    h,w=a.shape[:2]; yy,xx=np.ogrid[-1:1:complex(h), -1:1:complex(w)]
    lum=soft_luma(a)
    q=p['l5_velvet_amber']/100.0
    if q: a=add_tint(a,[0.82,0.56,0.28],q*0.28,mask=np.clip(1-np.abs(lum-.50)/.50,0,1))
    q=p['l5_lacquer_red']/100.0
    if q: a=add_tint(a,[0.72,0.30,0.22],q*0.22)
    q=p['l5_chandelier_halation']/100.0
    if q:
        br=np.clip((lum-.58)/.42,0,1)[...,None]
        warm=blur(a,max(2,min(h,w)*.016))
        warm[...,2]*=.72
        a=np.clip(a+warm*br*q*0.22,0,1)
    q=p['l5_wallpaper_mute']/100.0
    if q:
        hsv=rgb_to_hsv(a); hsv[...,1]*=(1-q*0.35); a=hsv_to_rgb(hsv)
    q=p['l5_corridor_depth']/100.0
    if q:
        center=np.exp(-((xx/0.62)**2+((yy+0.10)/1.35)**2))
        a*=1-(1-center)[...,None]*q*0.14
    q=p['l5_bar_smoke']/100.0
    if q:
        veil=np.clip((yy+1.2)/2.2,0,1)
        a=np.clip(a*(1-q*0.12)+np.array([0.54,0.47,0.41],dtype=np.float32)*q*0.12*veil[...,None],0,1)
    q=p['l5_carpet_crush']/100.0
    if q:
        floor=np.clip((yy+0.08)/1.08,0,1)
        a[...,0]=np.clip(a[...,0]*(1-floor*q*0.10),0,1)
        a[...,1]=np.clip(a[...,1]*(1-floor*q*0.16),0,1)
    q=p['l5_mirror_smear']/100.0
    if q:
        shifted=np.roll(blur(a,max(1,min(h,w)*.005)), max(1,int(w*0.008)), axis=1)
        br=np.clip((lum-.45)/.55,0,1)[...,None]
        a=np.clip(a*(1-q*0.12)+shifted*(q*0.12)*br,0,1)
    q=p['l5_ballroom_gold']/100.0
    if q: a=add_tint(a,[0.90,0.72,0.28],q*0.22,mask=np.clip((lum-.40)/.60,0,1))
    q=p['l5_haunted_glow']/100.0
    if q:
        ghost=np.roll(blur(a,max(2,min(h,w)*.012)), max(1,int(w*0.004)), axis=1)
        a=np.clip(a*(1-q*0.10)+ghost*(q*0.10),0,1)
    return a

def apply_album_covers(a,p):
    h,w=a.shape[:2]; yy,xx=np.ogrid[-1:1:complex(h), -1:1:complex(w)]
    lum=soft_luma(a)
    q=p['ac_varnish_amber']/100.0
    if q: a=add_tint(a,[0.86,0.74,0.50],q*0.28,mask=np.clip((lum-.15)/.85,0,1))
    q=p['ac_patina_olive']/100.0
    if q: a=add_tint(a,[0.52,0.55,0.36],q*0.22,mask=np.clip((.68-lum)/.68,0,1))
    q=p['ac_canvas_flatten']/100.0
    if q:
        low=blur(a,max(2,min(h,w)*.012)); a=np.clip(a*(1-q*0.28)+low*(q*0.28),0,1)
    q=p['ac_pigment_fade']/100.0
    if q:
        earth=np.array([0.58,0.52,0.46],dtype=np.float32)
        a=np.clip(a*(1-q*0.20)+earth*q*0.20,0,1)
    q=p['ac_repro_blur']/100.0
    if q:
        a=np.clip(a*(1-q*0.20)+blur(a,max(2,min(h,w)*.01))*(q*0.20),0,1)
    q=p['ac_gallery_shadow']/100.0
    if q:
        side=np.clip(np.abs(xx)/1.0,0,1)**1.6
        a*=1-side[...,None]*q*0.18
    q=p['ac_frame_falloff']/100.0
    if q:
        edge=np.clip((np.maximum(np.abs(xx),np.abs(yy))-.45)/.55,0,1)
        a*=1-edge[...,None]*q*0.20
    q=p['ac_detail_erosion']/100.0
    if q:
        smooth=blur(a,max(2,min(h,w)*.016)); mask=np.clip(1-np.abs(lum-.5)/.5,0,1)
        a=np.clip(a*(1-q*0.22*mask[...,None])+smooth*(q*0.22*mask[...,None]),0,1)
    q=p['ac_memory_smear']/100.0
    if q:
        smear=np.roll(blur(a,max(1,min(h,w)*.006)), max(1,int(w*0.006)), axis=1)
        a=np.clip(a*(1-q*0.16)+smear*(q*0.16),0,1)
    q=p['ac_oil_darkening']/100.0
    if q:
        sh=np.clip((.55-lum)/.55,0,1)
        a=add_tint(a,[0.28,0.22,0.18],q*0.24,mask=sh)
    q=p['ac_clouded_highlights']/100.0
    if q:
        hi=np.clip((lum-.48)/.52,0,1)
        a=np.clip(a*(1-hi[...,None]*q*0.10)+np.array([0.88,0.85,0.78],dtype=np.float32)*hi[...,None]*q*0.10,0,1)
    q=p['ac_sepia_dust']/100.0
    if q:
        a=add_tint(a,[0.70,0.57,0.41],q*0.18)
    q=p['ac_figure_obscurity']/100.0
    if q:
        center=np.exp(-((xx/0.7)**2+(yy/0.7)**2))
        a=np.clip(a*(1-center[...,None]*q*0.10)+blur(a,max(1,min(h,w)*.02))*center[...,None]*q*0.10,0,1)
    q=p['ac_print_bleed']/100.0
    if q:
        bleed=np.roll(a,1,axis=1); a=np.clip(a*(1-q*0.08)+bleed*(q*0.08),0,1)
    q=p['ac_quiet_space']/100.0
    if q:
        outer=np.clip((np.sqrt((xx*.9)**2+(yy*1.1)**2)-.15)/.95,0,1)
        a*=1-outer[...,None]*q*0.16
        gray=soft_luma(a)[...,None]
        a=np.clip(a*(1-outer[...,None]*q*0.06)+gray*(outer[...,None]*q*0.06),0,1)
    return a

def apply_institutional(a,p):
    if not any(v for k,v in p.items() if k.startswith("inst_")): return a
    h,w=a.shape[:2]; yy,xx=np.ogrid[-1:1:complex(h), -1:1:complex(w)]
    lum=soft_luma(a); field=lowfreq_field(h,w,81,65)
    q=p['inst_white_tube']/100.0
    if q: a=scale_color(a,[0.96,1.02,1.02],q*0.25,mask=np.clip((lum-.35)/.65,0,1))
    q=p['inst_ballast_roll']/100.0
    if q:
        bands=(np.sin(np.linspace(0,2*np.pi*10,h,dtype=np.float32))[:,None]*0.5+0.5)
        a[...,1]=np.clip(a[...,1]+bands*q*0.04,0,1)
    q=p['inst_chalky_paint']/100.0
    if q:
        m=np.clip((lum-.22)/.78,0,1)
        gray=lum[...,None]
        a=np.clip(a*(1-q*0.18*m[...,None])+gray*(q*0.18*m[...,None]),0,1)
    q=p['inst_wax_floor']/100.0
    if q:
        floor=np.clip((yy+0.12)/1.12,0,1)*np.clip((lum-.14)/.86,0,1)
        a=add_tint(a,[0.58,0.67,0.73],q*0.16,mask=floor)
        a=np.clip(a+blur(a,max(1,min(h,w)*.006))*floor[...,None]*q*0.08,0,1)
    q=p['inst_exit_sign_bleed']/100.0
    if q:
        green=np.clip(a[...,1]-a[...,0],0,1)
        a=add_tint(a,[0.28,0.76,0.36],q*0.16,mask=green)
    q=p['inst_beige_absorb']/100.0
    if q:
        target=np.array([0.72,0.68,0.60],dtype=np.float32)
        a=np.clip(a*(1-q*0.16)+target*q*0.16,0,1)
    q=p['inst_tile_coldness']/100.0
    if q: a=add_tint(a,[0.58,0.72,0.86],q*0.16)
    q=p['inst_office_green']/100.0
    if q: a=add_tint(a,[0.54,0.68,0.52],q*0.16)
    q=p['inst_hospital_blue']/100.0
    if q: a=add_tint(a,[0.48,0.62,0.84],q*0.16,mask=np.clip((lum-.20)/.80,0,1))
    q=p['inst_ceiling_deadzone']/100.0
    if q:
        top=np.clip(1-((yy+1)/2),0,1)
        a*=1-top[...,None]*q*0.08
    q=p['inst_corner_pressure']/100.0
    if q:
        r=np.sqrt((xx*0.95)**2+(yy*1.05)**2)
        edge=np.clip((r-.25)/.75,0,1)
        a*=1-edge[...,None]*q*0.14
    q=p['inst_mercury_pulse']/100.0
    if q:
        field2=lowfreq_field(h,w,82,35)
        a[...,2]=np.clip(a[...,2]+q*0.05*field2,0,1)
    q=p['inst_cleaner_residue']/100.0
    if q:
        haze=np.clip(field-.5,0,1)*np.clip((yy+0.2)/1.2,0,1)
        a=np.clip(a*(1-q*0.08*haze[...,None])+0.80*q*0.08*haze[...,None],0,1)
    q=p['inst_drained_daylight']/100.0
    if q:
        a=np.clip(a*(1-q*0.08)+soft_luma(a)[...,None]*q*0.08,0,1)
    q=p['inst_corridor_distance']/100.0
    if q:
        center=np.exp(-((xx/0.48)**2+((yy+0.1)/1.25)**2))
        a*=1-(1-center)[...,None]*q*0.12
    return a

from album_catalog import all_album_defaults
from era_catalog import all_era_defaults
DEFAULTS.update(all_album_defaults())
DEFAULTS.update(all_era_defaults())


# --- main render --------------------------------------------------------------
def render(rgb,settings=None,geometry=None,*,source_linear=False,out_bits=8,fast=False,album_id="none",era_id="none",level_id="l0"):
    """Return accurately typed 8/16-bit RGB output."""
    p = DEFAULTS | dict(settings or {})
    if any(not np.isfinite(v) for v in p.values()):
        raise ValueError('Invalid adjustment: non-finite number')
    a=normalized(rgb)
    if not source_linear:
        a=to_linear(a)
    a*=np.float32(2.0**p['exposure'])
    if source_linear:
        a=a/(1+.25*np.maximum(a-.7,0))
    a=to_srgb(a)

    # core tonal and color controls
    t=p['temperature']*.0022; ti=p['tint']*.0017
    a[...,0]*=1+t+.28*ti; a[...,1]*=1-.35*ti; a[...,2]*=1-t+.28*ti
    a=np.clip(a,0,4)
    lum=soft_luma(a)
    a+=p['shadows']/100*.36*np.power(np.clip(1-lum,0,1),2)[...,None]
    a+=p['highlights']/100*.36*np.power(np.clip(lum,0,1),2)[...,None]
    a+=(p['blacks']/100*.12)*np.power(np.clip(1-lum,0,1),3)[...,None]
    a+=(p['whites']/100*.12)*np.power(np.clip(lum,0,1),3)[...,None]
    a=(a-.45)*(1+p['contrast']/115.0)+.45
    a=np.clip(a,0,1)
    a=apply_tone_curve(a,p)

    hsv=rgb_to_hsv(a)
    if p['saturation']:
        hsv[...,1]*=max(0,1+p['saturation']/100.0)
    if p['vibrance']:
        hsv[...,1]*=np.maximum(0,1+p['vibrance']/100.0*(1-hsv[...,1]))
    hsv[...,1]=np.clip(hsv[...,1],0,1); hsv[...,2]=np.clip(hsv[...,2],0,1)
    a=hsv_to_rgb(hsv)

    # split-toning wheels
    if any(p[k] for k in ('shadow_strength','mid_strength','highlight_strength')):
        l=soft_luma(a)
        for area,mask in [
            ('shadow',np.clip((.55-l)/.55,0,1)),
            ('mid',1-np.clip(np.abs(l-.5)/.5,0,1)),
            ('highlight',np.clip((l-.45)/.55,0,1)),
        ]:
            strength=p[f'{area}_strength']/100.0
            if not strength: continue
            hue=math.radians(p[f'{area}_hue'])
            tint=np.array([
                .5+.5*math.cos(hue),
                .5+.5*math.cos(hue-2*math.pi/3),
                .5+.5*math.cos(hue+2*math.pi/3)
            ],dtype=np.float32)
            a=np.clip(a+(tint-.5)*mask[...,None]*strength*.28,0,1)

    if p['denoise'] and not fast:
        import cv2
        d=5 if p['denoise']<60 else 7
        filt=cv2.bilateralFilter(np.ascontiguousarray(a,dtype=np.float32), d,
                                 max(.005,p['denoise']*.0018), max(1,p['denoise']*.022))
        q=p['denoise']/100.0; a=a*(1-q)+filt*q
    if p['clarity']:
        b=blur(a,max(1,min(a.shape[:2])*.006))
        a=np.clip(a+(a-b)*p['clarity']/115.0,0,1)
    if p['dehaze']:
        amt=p['dehaze']/100.0
        a=np.clip((a-.48)*(1+amt*.55)+.48-amt*.035,0,1)
    if p['sharpen']:
        b=blur(a,1.1)
        a=np.clip(a+(a-b)*p['sharpen']/55.0,0,1)

    # specialized workspace controls
    level_ops={'l0':apply_level0,'l1':apply_level1,'l4':apply_level4,'l5':apply_level5}
    if level_id in level_ops:
        a=level_ops[level_id](a,p)
    a=apply_institutional(a,p)
    from specialist import process_caretaker, process_era
    a=process_caretaker(a,p,album_id=album_id)
    a=process_era(a,p,era_id=era_id)

    # geometry after grading
    a=np.clip(a,0,1).astype(np.float32,copy=False)
    if geometry:
        a=geometry_transform(a, geometry)

    if out_bits == 16:
        return np.uint16(np.clip(a,0,1)*65535.0+0.5)
    if out_bits == 8:
        return np.uint8(np.clip(a,0,1)*255.0+0.5)
    raise ValueError('out_bits must be 8 or 16')
