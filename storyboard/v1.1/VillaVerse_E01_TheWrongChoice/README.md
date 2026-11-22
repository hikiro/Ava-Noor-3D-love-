# VILLA VERSE — THE WRONG CHOICE / E01 v1.1

A reproducible 30-second reality-villa short storyboard. It includes the script, detailed shot plan, sixteen first/last drawn frames, four contact sheets, a fictional world layout, cast designs, separate 2D vector sprites, background assets, prop sheet, subtitles and a QA report.

## Open first
1. `storyboard_viewer.html` (open in browser; images are local, no network).
2. `EPISODE_SCRIPT_AND_SHOTPLAN.md` (timed script, camera, performances, world, sound, physical staging).
3. `storyboards/` (four large PNG comparison boards).
4. `assets/` (the image-generation design master, reusable vector blocking elements and world assets).
5. `CONTINUITY_AND_QA.md` (confirmed checks and limitations).

## Reproduce vectors

With Python, Pillow, and CairoSVG installed:

`python source/render_storyboard.py`

This regenerates 16 PNG+SVG storyboard keyframes, 4 storyboard sheets, sprites and background assets. PNGs and SVGs already ship ready to view; regenerating is not required. Font fallback is included for machines without DejaVu Sans; CairoSVG may require native Cairo dependencies on Windows.

## What this package is / is not

**Is:** a complete still storyboard and blocking kit with production notes for a fictional 30-second reel.
**Is not:** a finished animated video; a production-ready 3D character rig; physically validated acting; a pixel-art asset set; a voice/music license package.

## Source and provenance

- Story, scene design, assets, vector drawing source and shot timing: original material developed within this ChatGPT request.
- Established recurring character names and two-house continuity: from the prior Villa Verse planning thread.
- `assets/character_design_master.png`: AI-generated concept art image that defines the desired 2.5D look and wardrobe.
- All other assets: rendered with included Python/SVG code, no external photos, fonts, libraries or 3D models bundled.
- Four unrelated generated image results from earlier attempts were rejected and are not in this archive.
