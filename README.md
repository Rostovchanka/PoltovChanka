# ELSEWHERE STUDIO — Caretaker / Eras Edition (0.8.0)

A Windows-first desktop photo editor dedicated to developing **your own photographs** into convincing liminal images. No image-generation features, pasted assets, brushes, painted gradients, stock textures, or perspective correction.

## Dedicated horizontal workspaces

**Backrooms** — four nested laboratories (Level 0, Level 1, Level 4, Level 5), each with **10 individually editable controls and a description for every setting**. Selecting a level only chooses its adjustment bank; it does not apply a preset.

**Album Covers** — 22 named releases/stages from **The Caretaker** discography, with real album names and painting titles where verified. Each selected album offers **5 edition-specific photographic controls + 15 common print/paint/memory controls**. Changing the selected album does not apply a grade on its own. Artwork is researched in `COVER_RESEARCH.md`; copyrighted cover art is not embedded or pasted into photographs.

**Institutional** — 15 controls for empty offices, fluorescent halls, parking corridors, schools, hospitals and institutional surfaces.

**Temporal** — **exactly five photographic eras**: 1970s, 1980s, 1990s, 2000s, 2010s. **15 individually described controls per era**, no generic preset buttons. The effects operate on the pixels in the user's photo.

**Core**, **Geometry**, **RAW Settings** — preserve the technical editing foundation. Only one Backrooms level, one Caretaker cover, and one Temporal era are active at a time. Their slider values remain saved when switching between modes.

## Actual file support

- Canon CR3, CR2, DNG and other RAW formats supported by the installed LibRaw/rawpy build
- JPG / JPEG
- PNG (including 16-bit RGB)
- TIFF (including 16-bit RGB)

The **same post-decode adjustment operations** are available for all formats. RAW-only exceptions concern sensor decoding (white balance and highlight modes). JPEG files cannot recover data absent from the original JPEG. 16-bit input → float32 processing → genuine 16-bit PNG/TIFF export. JPEG export is 8-bit. The source file is protected against export overwrite.

## Windows standalone executable (no Python required to *run*)

This downloaded ZIP is the build project, **not** an already compiled EXE. The chat environment is Linux and cannot directly verify a Windows executable.

**Build without installing Python:**
1. Upload/replace the project files in your existing GitHub repository, keeping `.github/workflows/windows-portable.yml` in that folder.
2. Open GitHub **Actions → Build Standalone Elsewhere for Windows → Run workflow**.
3. When the Windows build succeeds, download the **Elsewhere-Studio-Windows-Portable** artifact.
4. Extract its archive. Launch `Elsewhere Studio.exe` inside the application folder.
5. Keep the whole portable application folder together. **Python is bundled** in the finished build and not needed on the target computer.

Alternatively, an installed Python **3.11** can compile the application locally using `BUILD_WINDOWS.cmd`.

## Engineering limits

- The 16-bit pipeline uses sRGB output rather than a complete per-camera color-management/calibration system.
- Performance with full-resolution EOS R5 45-MP files has not been measured on your Windows machine. Full-res float32 processing can be memory intensive.
- Qt GUI functionality and actual R5 `.CR3` opening must be checked using the compiled Windows build; the available Linux environment lacks PySide6.
- A Caretaker cover’s pictorial composition cannot be generated from a different photograph using color processing alone. The controls seek *color, tonal, and pictorial response* without creating objects or copyrighted artwork.
