"""Photo-development controls organized into exactly five eras.

The historical labels are visual approximations, not claims that a decade had a
single photographic look. All adjustments operate on the user's pixels.
"""
ERAS={
 '1970s': {
  'summary':'Color-negative film, photochemical print response, tungsten interiors and warm shadow chemistry. No prebuilt grain/texture overlays.',
  'palette':(0.90,0.72,0.54),
  'controls':[
   ('70_dye_warm','Dye-layer warmth','Bias existing midtones toward the warm dye balance of 1970s consumer color prints.'),
   ('70_tungsten','Tungsten shoulder','Saturate warm highlights while compressing their headroom.'),
   ('70_magenta_loss','Magenta dye loss','Reduce magenta separation in the highs to simulate selective dye aging.'),
   ('70_green_heel','Green shadow heel','Shape the green channel near the photographic black floor.'),
   ('70_film_toe','Negative-film toe','Round shadow gradation without simply raising overall exposure.'),
   ('70_film_shoulder','Film shoulder','Compress the upper tonal shoulder with a smooth transfer.'),
   ('70_amber_flash','Amber flash','Alter high-frequency highlight chroma toward incandescent warmth.'),
   ('70_chroma_grain','Chroma grain coupling','Noise responds to photographic midtone luminance, generated only from existing pixels.'),
   ('70_lens_milk','Milky lens','Reduce microcontrast around high luminance rather than applying global blur.'),
   ('70_print_paper','Paper white','Reduce the pure-white point toward warmed photographic paper.'),
   ('70_orange_mask','Orange negative mask','Rotate warm channel relationships selectively.'),
   ('70_skinless_green','Green dye subtraction','Dampen overdominant cyan/green in neutral interior surfaces.'),
   ('70_aged_chemistry','Chemistry crossover','Introduce opposing shadow and highlight dye-color responses.'),
   ('70_dustless_matte','Soft matte','Flatten the lowest density zone without painting artifacts.'),
   ('70_print_distance','Print-distance separation','Gently compress distant-looking low-detail regions.'),
  ]
 },
 '1980s': {
  'summary':'Consumer color print, cold commercial fluorescents, early video/telecine tonality and fluorescent/mixed-light contamination.',
  'palette':(0.53,0.66,0.80),
  'controls':[
   ('80_cyan_shadow','Cyan shadow balance','Pull deep shadow chroma toward cold commercial print balance.'),
   ('80_tungsten_mix','Mixed tungsten','Let warm lights push against otherwise cool interiors.'),
   ('80_telecine_heel','Telecine blacks','Use a low-luminance video transfer resembling analog transfer.'),
   ('80_broadcast_white','Broadcast white ceiling','Soften highs before they become harsh video white.'),
   ('80_fluor_green','Office fluorescent spill','Bias cold upper midtones toward fluorescent green.'),
   ('80_blue_pop','Electric blue separation','Separate blue chroma from gray midtone surroundings.'),
   ('80_analog_y','Analog luminance bleed','Smooth brightness detail differently from the chroma channels.'),
   ('80_chroma_delay','Chrominance delay','Small lateral displacement of chroma, not of architectural edges.'),
   ('80_paper_pink','Print pink fade','Add subtle print-process pink into neutral highlights.'),
   ('80_hard_flash','Flash hardening','Increase bright-region local contrast without boosting the whole image.'),
   ('80_soft_broadcast','Broadcast diffusion','Suppress fine detail only where luminance is high.'),
   ('80_early_ccd','Video sensor coolness','Shift green/blue separation in middle luminance.'),
   ('80_silver_black','Silver-black density','Shape dark regions with a slightly denser channel response.'),
   ('80_saturation_cap','Chroma cap','Prevent saturated colors from overpowering a restrained image.'),
   ('80_retake','Analog transfer repetition','Small, source-derived luma echo rather than pasted textures.'),
  ]
 },
 '1990s': {
  'summary':'High-street minilab prints, compact-film cameras, on-camera flash, beige indoor casts and consumer print-scanner color.',
  'palette':(0.73,0.66,0.59),
  'controls':[
   ('90_minilab_beige','Minilab paper beige','Move photographed whites toward a warm consumer-photo stock response.'),
   ('90_flash_core','Compact-camera flash','Increase bright-region center contrast while maintaining image boundaries.'),
   ('90_green_print','Green lab chemistry','Bias neutral whites toward slight laboratory green.'),
   ('90_purple_shadow','Magenta shadow shift','Shift low lights in the green-magenta axis.'),
   ('90_baby_blue','Pocket-camera blue','Separate pale cool surfaces from warmer ambient light.'),
   ('90_soft_high','Print highlight softness','Round overexposed print highlights.'),
   ('90_pocket_lens','Pocket-lens microcontrast','Reduce very fine detail without simulating heavy blur.'),
   ('90_minilab_toe','Minilab toe','Give shadows a compressed print density.'),
   ('90_silver_shift','Scanner black bias','Change low-density black balance by channel.'),
   ('90_overfill','Overfilled flash whites','Shape the high-end shoulder as a mild flash hotspot.'),
   ('90_print_luma','Color paper luminance','Reduce overly clinical midtone spacing.'),
   ('90_chroma_corner','Corner chroma drift','Change peripheral chroma without adding a vignette sticker.'),
   ('90_highlight_blue','Cool lab highlights','Add a gentle cold countercast to brighter regions.'),
   ('90_film_density','Print density','Deepen the image in a gradual film-curve fashion.'),
   ('90_repeat_print','Copy-of-a-copy','Apply a low-amplitude, source-derived photographic registration drift.'),
  ]
 },
 '2000s': {
  'summary':'Compact digital-camera CCD tonality, early automatic white balance, direct flash, strong local contrast and small-camera highlights.',
  'palette':(0.55,0.67,0.78),
  'controls':[
   ('00_ccd_cyan','CCD cyan','Bias bright blue/green separation of early digital cameras.'),
   ('00_flash_shoulder','Point-and-shoot flash','Simulate abrupt highlight compression around small-camera flash reflections.'),
   ('00_blue_dark','Blue digital shadows','Push low luminance toward blue without changing neutral whites.'),
   ('00_cold_wb','Cold auto-white-balance','Shift neutral image areas toward a cool AWB error.'),
   ('00_ccd_noise','CCD chroma response','Chroma contamination that increases with low-light regions.'),
   ('00_sharpen_rim','In-camera edge sharpening','Local edge contrast reminiscent of consumer digital signal processing.'),
   ('00_hard_mid','Small-sensor midcontrast','Increase contrast primarily in the midtones.'),
   ('00_white_clip','Digital white clipping','Compress extreme highlights more abruptly than film-like rolloff.'),
   ('00_green_cast','Indoor digital green','Increase green bias in artificial-lit midtones.'),
   ('00_magenta_low','Purple low-light cast','Reduce low-light color neutrality.'),
   ('00_chroma_crosstalk','CCD channel crosstalk','Mix RGB channels subtly in medium contrast areas.'),
   ('00_flash_falloff','Flash center falloff','Change brightness according to image position and source highlights.'),
   ('00_cheap_lens','Compact lens softness','Mild nonlinear microcontrast falloff toward the edges.'),
   ('00_saturation_knuckle','JPEG saturation shoulder','Cap intense consumer-camera hues.'),
   ('00_digicam_flat','Bright-camera tonal plate','Move high-key neutral interiors toward an early-digital tonal arrangement.'),
  ]
 },
 '2010s': {
  'summary':'Early smartphone HDR, aggressive local contrast, shadow lifting, bright white points and clean but processed digital color.',
  'palette':(0.64,0.72,0.77),
  'controls':[
   ('10_phone_hdr','Phone HDR lift','Raise low-luminance areas while retaining the photographed highlight zones.'),
   ('10_clarity_micro','Mobile microcontrast','Add restrained local contrast to architectural detail.'),
   ('10_blue_clean','Clean blue-white','Shift pale surfaces toward smartphone auto white balance.'),
   ('10_sky_cyan','Early app cyan','Target existing blue hues with a colder photo-app cast.'),
   ('10_warm_high','Warm highlight toning','Introduce photographic-app warmth in bright tones.'),
   ('10_shadow_clean','Noise-smoothed shadows','Reduce low-light high-frequency variation.'),
   ('10_white_pop','Smartphone white point','Raise upper midtones without overexposing the full frame.'),
   ('10_filter_matte','Mobile filter matte','Compress black shadows with smooth app-style print response.'),
   ('10_edge_pop','Mobile edge pop','Strengthen image edges without inventing structure.'),
   ('10_chroma_clean','Chroma clean-up','Reduce saturated shadow noise while retaining core colors.'),
   ('10_vsco_cool','Cool mobile preset chemistry','Bias neutrals toward a clean, muted cyan-gray response.'),
   ('10_amber_skinless','Ambient warmth','Apply an amber chromatic response to existing warm illumination only.'),
   ('10_tone_map','Compact tone-map compression','Lower highlight/shadow contrast difference.'),
   ('10_bright_flat','App-level bright flatness','Smooth very bright walls and corridors.'),
   ('10_digital_fade','Digital fade','Narrow the final dynamic range slightly without nostalgic dust assets.'),
  ]
 }
}

def all_era_defaults():
    return {key:0. for era in ERAS.values() for key,_,_ in era['controls']}
