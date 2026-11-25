---
name: blender
description: Use when modeling, texturing, rigging, animating, lighting, rendering, reviewing or exporting Blender assets, matching reference images, or choosing a 3D art style. Automated operations require Blender and a connected Blender MCP server; without MCP, provide plans or bpy scripts for the user to run.
license: MIT
---

# Blender

Use this entry to load relevant production and art-direction guidance from the 94 bundled reference documents.

## Start with the task

- For a new asset, reference-image match, or a task spanning several disciplines, read [blender-director](guides/blender-director/guide.md) first, then the relevant discipline guides.
- For a focused operation, open its guide directly from the index below. Load a style, mood or game-genre guide only when it matches the requested direction.
- For engine delivery, load the target engine guide plus [export-pipeline](guides/export-pipeline/guide.md), and complete [asset-optimization](guides/asset-optimization/guide.md) before exporting.
- When a guide mentions another skill by name, find its guide in this index. Relative `references/` paths belong to that guide; `../references/` points to the shared production references.
- Read [MCP integration](guides/references/mcp-integration.md) before automated Blender operations. Inspect the available tools, execute through supported operations, and verify the actual scene or output.

## Requirements

The upstream setup guide specifies Blender 3.0+, Python 3.10+ (3.11 recommended), uv, and the BlenderMCP add-on/server connected to Blender (default localhost:9876). See [setup](docs/BLENDER_MCP_SETUP.md). An already connected compatible Blender MCP is sufficient; do not silently install or change the user's configuration.

If MCP is unavailable, provide concise planning and Python `bpy` scripts the user can run, and explain which scene checks remain unverified. Sketchfab, Hyper3D, Hunyuan3D and Poly Haven integrations are optional. These guides contain no executable helper scripts.

## Complete guide index

### Production and validation

- [asset-optimization](guides/asset-optimization/guide.md)
- [blender-director](guides/blender-director/guide.md)
- [blender-modeler](guides/blender-modeler/guide.md)
- [qa-review](guides/qa-review/guide.md)

### Modeling

- [character-artist](guides/character-artist/guide.md)
- [creature-artist](guides/creature-artist/guide.md)
- [environment-artist](guides/environment-artist/guide.md)
- [geometry-nodes](guides/geometry-nodes/guide.md)
- [hard-surface](guides/hard-surface/guide.md)
- [procedural-modeling](guides/procedural-modeling/guide.md)
- [prop-artist](guides/prop-artist/guide.md)
- [retopology](guides/retopology/guide.md)
- [sculpting](guides/sculpting/guide.md)
- [vegetation-artist](guides/vegetation-artist/guide.md)
- [vehicle-artist](guides/vehicle-artist/guide.md)

### Surfaces and textures

- [lookdev](guides/lookdev/guide.md)
- [materials](guides/materials/guide.md)
- [texture-workflow](guides/texture-workflow/guide.md)
- [uv-workflow](guides/uv-workflow/guide.md)

### Animation and simulation

- [animation](guides/animation/guide.md)
- [cloth-sim](guides/cloth-sim/guide.md)
- [hair-groom](guides/hair-groom/guide.md)
- [physics-sim](guides/physics-sim/guide.md)
- [rigging](guides/rigging/guide.md)

### Scenes, cameras and rendering

- [camera-cinematography](guides/camera-cinematography/guide.md)
- [compositing](guides/compositing/guide.md)
- [lighting](guides/lighting/guide.md)
- [rendering](guides/rendering/guide.md)
- [scene-assembly](guides/scene-assembly/guide.md)
- [set-dressing](guides/set-dressing/guide.md)
- [vfx-fx](guides/vfx-fx/guide.md)

### Engine delivery

- [collision-proxy](guides/collision-proxy/guide.md)
- [export-pipeline](guides/export-pipeline/guide.md)
- [godot-export](guides/godot-export/guide.md)
- [lod-pipeline](guides/lod-pipeline/guide.md)
- [unity-export](guides/unity-export/guide.md)
- [unreal-export](guides/unreal-export/guide.md)

### Visual styles

- [analog-found-footage-horror](guides/analog-found-footage-horror/guide.md)
- [anime-style](guides/anime-style/guide.md)
- [archviz](guides/archviz/guide.md)
- [body-horror-style](guides/body-horror-style/guide.md)
- [cartoon-style](guides/cartoon-style/guide.md)
- [chibi-style](guides/chibi-style/guide.md)
- [comic-book-style](guides/comic-book-style/guide.md)
- [cosmic-eldritch-horror](guides/cosmic-eldritch-horror/guide.md)
- [dream-weirdcore-style](guides/dream-weirdcore-style/guide.md)
- [folk-horror-style](guides/folk-horror-style/guide.md)
- [frutiger-aero-style](guides/frutiger-aero-style/guide.md)
- [hand-painted-style](guides/hand-painted-style/guide.md)
- [hd-2d-style](guides/hd-2d-style/guide.md)
- [horror-style](guides/horror-style/guide.md)
- [indie-horror-aesthetics](guides/indie-horror-aesthetics/guide.md)
- [isometric-style](guides/isometric-style/guide.md)
- [liminal-space-style](guides/liminal-space-style/guide.md)
- [lowpoly-style](guides/lowpoly-style/guide.md)
- [manga-style](guides/manga-style/guide.md)
- [mascot-puppet-horror](guides/mascot-puppet-horror/guide.md)
- [minimalist-style](guides/minimalist-style/guide.md)
- [neon-retrofuturism](guides/neon-retrofuturism/guide.md)
- [noir-style](guides/noir-style/guide.md)
- [painterly-style](guides/painterly-style/guide.md)
- [pixel-art-style](guides/pixel-art-style/guide.md)
- [psx-horror-style](guides/psx-horror-style/guide.md)
- [realistic-style](guides/realistic-style/guide.md)
- [retro-16bit-style](guides/retro-16bit-style/guide.md)
- [retro-8bit-style](guides/retro-8bit-style/guide.md)
- [stop-motion-craft-style](guides/stop-motion-craft-style/guide.md)
- [stylized-style](guides/stylized-style/guide.md)
- [vector-style](guides/vector-style/guide.md)
- [visual-console-eras](guides/visual-console-eras/guide.md)
- [voxel-style](guides/voxel-style/guide.md)

### Worlds, moods and game genres

- [apocalypse-worlds](guides/apocalypse-worlds/guide.md)
- [biome-worlds](guides/biome-worlds/guide.md)
- [brutalist-mood](guides/brutalist-mood/guide.md)
- [character-archetypes](guides/character-archetypes/guide.md)
- [cozy-wholesome-mood](guides/cozy-wholesome-mood/guide.md)
- [dark-gritty-mood](guides/dark-gritty-mood/guide.md)
- [dream-surreal-mood](guides/dream-surreal-mood/guide.md)
- [fantasy-worlds](guides/fantasy-worlds/guide.md)
- [genre-action-combat](guides/genre-action-combat/guide.md)
- [genre-card-party-idle](guides/genre-card-party-idle/guide.md)
- [genre-metroidvania-roguelike](guides/genre-metroidvania-roguelike/guide.md)
- [genre-narrative-vn](guides/genre-narrative-vn/guide.md)
- [genre-open-world-sandbox](guides/genre-open-world-sandbox/guide.md)
- [genre-puzzle-platformer](guides/genre-puzzle-platformer/guide.md)
- [genre-racing-sports](guides/genre-racing-sports/guide.md)
- [genre-rpg](guides/genre-rpg/guide.md)
- [genre-shooter](guides/genre-shooter/guide.md)
- [genre-soulslike](guides/genre-soulslike/guide.md)
- [genre-stealth](guides/genre-stealth/guide.md)
- [genre-strategy-sim](guides/genre-strategy-sim/guide.md)
- [genre-survival](guides/genre-survival/guide.md)
- [historical-worlds](guides/historical-worlds/guide.md)
- [sci-fi-punk-worlds](guides/sci-fi-punk-worlds/guide.md)
