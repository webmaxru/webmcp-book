# Figure kit

Every figure is a hand-written SVG in `figures/src/figure-N-M.svg` (A–D for appendices), rendered to
`manuscript/resources/images/figure-N-M.png` (2400 px wide, white background) by `python3 figures/render.py`.
The PNG is what the manuscript references, so Leanpub, KDP and EPUB all get a plain raster image.
Figures carry no "Figure N.M" title inside the image: the caption lives in the manuscript.

Use these values only (from the APM book theme, light mode):

| Role | Value |
|---|---|
| background | #FFFFFF (canvas), panels #F6F7FB or #EEF1F8 |
| text | #171A22, secondary #5A6478 |
| strokes / borders | #DCE1EC (light), #5A6478 (emphasis) |
| primary accent (the page / the site / "human") | indigo #5A54F0, strong #3F38D6, text on indigo #FFFFFF |
| second accent (the agent / the machine) | amber #B87613, strong #8F5A0C |
| third accent (browser / platform) | teal #0EA5A5 |
| fourth accent (risk / attacker / warning) | magenta #C2468A |
| dark code panel | #10141F with text #E6EAF6, keywords #9E98FF, strings #7FD0A6, numbers #E7B23D |

Type: `font-family="Bricolage Grotesque"` (weights 600–800) for titles and box labels, 22–30 px at a 1200 px
wide viewBox; `"IBM Plex Mono"` for code, API names and file names; `"Literata"` for small explanatory notes.
Rounded rectangles rx=14 (panels) or rx=9 (small boxes). Arrows: 2.5 px strokes, #5A6478, simple
triangular markers. No gradients, no drop shadows, no icons from icon fonts, no clip-art, no AI-generated
images. Keep it legible when printed at 5 in wide in greyscale (do not rely on colour alone).

viewBox width 1200; height whatever the content needs. Set width/height attributes equal to the viewBox.
