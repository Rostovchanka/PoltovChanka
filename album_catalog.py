"""Release-level catalogue for The Caretaker. Artwork images are NOT bundled.

Titles and release chronology checked against official Bandcamp, artist discography
and collector release listings. Not all early/obscure edition cover visuals are
verified; descriptions identify uncertainty instead of inventing cover details.
"""
from __future__ import annotations

# (id, release, date, visual description, artwork/painting title, palette sRGB,
#  featured release-specific control labels [5])
DATA = [
('haunted_ballroom','Selected Memories From The Haunted Ballroom','1999',
 'Archival, blue-monochrome ballroom photograph with dated print contrast and prominent typography.',
 'Photographic cover; edition artwork varies', (0.32,0.45,0.68),
 ['Orchestra cyanotype','Ballroom paper whites','Period-photo compression','Midnight-blue shadows','Archival separation']),
('stairway','A stairway to the stars','2001',
 'Early haunted-ballroom era sleeve. Edition artwork differs; designed here as a restrained low-light archival treatment.',
 'Artwork attribution: Andrew Cliff (early release)', (0.34,0.38,0.51),
 ['Ballroom cobalt','Ghost-room whites','Vintage paper fade','Dark-stage floor','Stairway isolation']),
('rainbow',"We'll all go riding on a rainbow",'2003',
 'Graphic ballroom silhouettes in electric blue/cyan, white and black; much higher contrast than the later oil paintings.',
 'Graphic ballroom illustration', (0.12,0.58,0.83),
 ['Electric-cyan silhouettes','Porcelain cutouts','Hard-black staging','Graphic midtone removal','Dance-floor separation']),
('anterograde','Theoretically pure anterograde amnesia','2005–2006',
 'Dark purple/blue abstract cover with a bright vertical highlight and fragmented text.',
 'Dark abstract photographic design', (0.32,0.21,0.55),
 ['Violet-blue fracture','Vertical-light bleach','Low-mid collapse','Indigo shadow mass','Abstraction separation']),
('additional','Additional amnesiac memories','2006',
 'Black-and-white reworking of a period ballroom-record image, visually linked to earlier Caretaker sleeves.',
 'Edited Take Your Partners photograph (attributed in discography)', (0.42,0.42,0.50),
 ['Amnesiac purple','Archival luminosity','Soft black suspension','Uncertain midtones','Companion-image isolation']),
('deleted','Deleted scenes, forgotten dreams','2007',
 'Painted cover by Guy Denning; figurative and emotionally charged, from the period before the Ivan Seal collaboration.',
 'the impossible dream (Guy Denning, 2006)', (0.45,0.33,0.36),
 ['Deleted-scene greys','Forgotten highlight','Muted print color','Shadow reservation','Empty-frame separation']),
('museum','Recollected memories from the Museum of Garden History','2008',
 'Live archival release; precise front-cover imagery is edition-dependent and not fully verified.',
 'Artwork not independently verified', (0.47,0.48,0.39),
 ['Museum olive','Archival white','Botanical matte','Display-case shadow','Historical isolation']),
('persistent','Persistent repetition of phrases','2008',
 'Dark blue-violet, nearly empty interior: a faint rectangular picture frame hanging on a softly lit wall.',
 'Empty frame / blue-wall artwork (painting title not verified)', (0.29,0.34,0.48),
 ['Blue frame illumination','Unoccupied wall whites','Violet interior cast','Empty-frame shadows','Frame isolation']),
('london','Recollections from old London town','2009',
 'Radio/compilation archive. No single fully verified front cover for all circulating editions.',
 'Artwork not independently verified', (0.48,0.44,0.37),
 ['Old-London brown','Fogged print white','Street-photo compression','Archive shadow','Distance isolation']),
('fact45','FACT Mix 45: The Caretaker — Delving Into My Past for FACT','2009',
 'Promotional FACT mix design in purple-black with title lettering; mixes can be circulated in alternate formats.',
 'FACT mix sleeve / magazine graphic', (0.38,0.37,0.44),
 ['FACT-era grey','Distant electric blue','Print loss','Deep archive blacks','Mix-cover isolation']),
('complete','The complete digital collection (1996–2008)','2009',
 'Collection edition: artwork and compilation packaging vary; no single sleeve is asserted here.',
 'Compilation cover varies', (0.43,0.42,0.42),
 ['Collected-neutral palette','Early/late contrast','Archive fade','Subdued history blacks','Collection isolation']),
('empty_bliss','An empty bliss beyond this World','2011',
 'Ivan Seal: large pale blue-grey spherical object and a tiny red-tipped match against a dark studio background.',
 'happy in spite (Ivan Seal)', (0.57,0.62,0.65),
 ['Pale plaster sphere','Match-point red','Blue-grey object','Dark studio backdrop','Object isolation']),
('patience','Patience (After Sebald)','2012',
 'Dark painted snow-globe/lighthouse study; reflective dome, muted ground and miniature interior.',
 'Ivan Seal glass-dome / lighthouse cover', (0.43,0.47,0.50),
 ['Snow-globe sheen','Lighthouse-white remnants','Glass darkness','Cold island ground','Dome isolation']),
('extra_patience','Extra Patience (After Sebald)','2012',
 'Companion dark-glass lighthouse cover with streaked/reflected marks around the dome.',
 'Ivan Seal glass-dome / lighthouse cover', (0.39,0.43,0.49),
 ['Dark glass reflections','Wet-dome streaks','Lighthouse remnant','Black-glass depth','Object isolation']),
('stage1','Everywhere at the end of time — Stage 1','2016',
 'Ivan Seal still life: folded, rolled grey paper or scroll-like object against a blue-to-green backdrop.',
 'Beaten Frowns After (Ivan Seal)', (0.38,0.51,0.57),
 ['Grey folded-paper tone','Sky-blue background','Muted green ground','Soft paper relief','Scroll-like isolation']),
('stage2','Everywhere at the end of time — Stage 2','2017',
 'Ivan Seal still life: wilting flowers in an ambiguous decaying vase on a pale green/beige background.',
 'Pittor Pickgown in Khatheinstersper (Ivan Seal)', (0.56,0.61,0.53),
 ['Wilted-petal pink','Corroded vase shadow','Pastel green surround','Faded plant relief','Bouquet isolation']),
('stage3','Everywhere at the end of time — Stage 3','2017',
 'Ivan Seal: dense tangled kelp/plant-like shape, deep near-black green against a pale cool field.',
 'Hag (Ivan Seal)', (0.35,0.45,0.43),
 ['Tangled deep green','Kelp-black lattice','Cool pale surround','Botanical detail loss','Growth isolation']),
('desert','Take care. It’s a desert out there…','2017',
 'Ivan Seal: pale grey abstract sculptural formation floating above a neutral light ground; the cover does not depict a literal desert.',
 'Pale abstract sculpture (Ivan Seal; painting title not verified)', (0.62,0.63,0.62),
 ['Pale sculpture greys','Soft white surround','Mineral midtones','Floating cast-shadow','Object isolation']),
('stage4','Everywhere at the end of time — Stage 4','2018',
 'Ivan Seal: blue-green disfigured human bust/profile with indistinct painted features.',
 'Giltsholder (Ivan Seal)', (0.30,0.48,0.49),
 ['Blue-green bust','Facial-form erosion','Oil-paint cobalt','Indistinct feature dark','Figure isolation']),
('stage5','Everywhere at the end of time — Stage 5','2018',
 'Ivan Seal: multicolored thickly painted abstract accumulation, heavily fragmented with muted pinks, blues and greens.',
 'Eptitranxisticemestionscers Desending (Ivan Seal)', (0.55,0.48,0.48),
 ['Impasto muted rose','Fragmented cold blues','Painted-edge erosion','Compressed pigment range','Mass isolation']),
('stage6','Everywhere at the end of time — Stage 6','2019',
 'Ivan Seal: pale ochre-brown upright board with a spare blue-tape frame against a muted green background.',
 'Necrotomigaud (Ivan Seal)', (0.52,0.49,0.37),
 ['Ochre board flatness','Blue-tape remnant','Moss-grey backdrop','Object paint loss','Board isolation']),
('everywhere_bliss','Everywhere, an empty bliss','2019',
 'Dense dark oil-painted abstract field, with entangled strokes of deep blue, near-black, olive and muted high-chroma flecks.',
 'Dark blue impasto abstract (Ivan Seal; edition variants)', (0.24,0.32,0.35),
 ['Deep blue impasto','Oil-black paint mass','Olive pigment flecks','Color fragment exhaustion','Abstract-field isolation']),
]

COVERS={}
for id_,title,year,description,artwork,palette,feature_names in DATA:
    COVERS[id_]={
        'title':title,'year':year,'description':description,
        'artwork':artwork,'palette':palette,
        'features':feature_names
    }

# Custom adjustments apply only when moved; choosing a release does not grade the photo.
ALBUM_CONTROLS=[
 ('ac_varnish_amber','Varnish response','Warm illuminated regions in proportion to their existing luminance.'),
 ('ac_patina_olive','Paint oxidation','Bias existing shadow chroma toward an oxidized green/olive response.'),
 ('ac_canvas_flatten','Paint-layer diffusion','Compress high-frequency pictorial information while keeping overall photographed composition.'),
 ('ac_pigment_fade','Pigment fatigue','Narrow the available color range toward an album-specific neutral.'),
 ('ac_repro_blur','Reproduction softness','Reproduce the low microcontrast of photographed paintings without adding texture assets.'),
 ('ac_gallery_shadow','Gallery falloff','Shape side-to-side black falloff associated with isolated painted objects.'),
 ('ac_frame_falloff','Frame compression','Gently reduce tonal separation near the image edges.'),
 ('ac_detail_erosion','Contour uncertainty','Soften small boundaries more strongly around the midtones.'),
 ('ac_memory_smear','Registration drift','Displace a fraction of the existing image laterally, as a subtle reprographic artifact.'),
 ('ac_oil_darkening','Varnished blacks','Darken existing low luminance regions with album-calibrated pigment bias.'),
 ('ac_clouded_highlights','Clouded lights','Compress bright regions toward the selected cover’s pale tonal color.'),
 ('ac_sepia_dust','Warm pigment undertone','Introduce a warm bias entirely from the photograph’s existing color data.'),
 ('ac_figure_obscurity','Subject ambiguity','Blur central fine detail slightly, without generating or hiding objects.'),
 ('ac_print_bleed','Print registration','Blend neighboring source pixels for tiny reproduction misalignment.'),
 ('ac_quiet_space','Negative-space silence','Reduce saturation and brightness outward from the center.'),
]

# Additional five controls per named artwork, tuned by that release profile.
FEATURE_DESCRIPTIONS=[
 'Blend existing hues toward this particular cover’s principal chromatic family.',
 'Tame high luminance so the photographed subject sits closer to its source cover’s bright tonal range.',
 'Compress midtones using the source cover’s signature chroma relationship.',
 'Reshape the shadow floor to match the apparent painted or printed depth.',
 'Separate the existing central subject from its background without replacing image content.',
]

def all_album_defaults():
    result={key:0. for key,_,_ in ALBUM_CONTROLS}
    for id_ in COVERS:
        for i in range(5):result[f'cover_{id_}_{i}']=0.
    return result
