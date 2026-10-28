"""Repeatable CPU-only renderer timing. Not a Lightroom comparison."""
import time
import platform
import numpy as np
from engine import render, DEFAULTS

def main():
    print('Elsewhere render benchmark |',platform.platform())
    rng=np.random.default_rng(21)
    for h,w in ((512,512),(1080,1440),(2200,3300)):
        rgb=rng.integers(0,65536,(h,w,3),dtype=np.uint16)
        for name,grade in [('neutral',DEFAULTS),('liminal',DEFAULTS|dict(l4_dead_air=25,l4_fluor_flatness=35,l4_beige_drain=30,clarity=12))]:
            start=time.perf_counter()
            image=render(rgb,grade,source_linear=False,out_bits=16,fast=True,level_id='l4')
            secs=time.perf_counter()-start
            print(f'{w}x{h}  {name}: {secs:.3f}s; output={image.dtype}')
if __name__=='__main__':main()
