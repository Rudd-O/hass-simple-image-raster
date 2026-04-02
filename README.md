# Simple image raster for Home Assistant

This repository contains an integration that provides an action for rendering
bitmap images or PDF documents.  It is useful standalone or in combination with
[IPP printing](https://github.com/Rudd-O/homeassistant-ipp-printing) as well as
other integrations that benefit from live image data.

With this integration, you can draw simple images based on a series of commands
you send to the drawing engine, and receive the rendered data.  The rendered
data can then be used in your scripts to change images in Home Assistant, send
updates to ePaper displays, or even directly print using the IPP printing integration
linked above.

This is a derivative work based on the [Home Assistant NIIMBOT](https://github.com/eigger/hass-niimbot)
integration.

## Installation

1. Install this integration with HACS (add this repository as an integration type
   repository to HACS).  Alternatively (not recommended), copy the
   `custom_components/ipp_printer` directory of this repository into your Home Assistant's configuration `custom_components` directory.
2. Restart Home Assistant..
3. Be sure you have already added at least one IPP printer to Home assistant using the
   IPP integration that ships with Home Assistant.
4. Go to **Settings** → **Integrations** and add integration **IPP printer**.
5. Confirm the dialog onscreen.

## Examples

See the [examples](examples/README.md) folder for examples of how to exploit this
integration usefully.

## Action: `simpleimageraster.draw`

This action allows you to draw images using simple commands.  When an
image is drawn, the return value (mandatory — you have to add a
response variable whenever you use it) contains a dictionary with:

* `data`: the image (base64-encoded) in the format you requested
* `mimetype`: the MIME type of the image

### Parameters

| Parameter  | Required | Default     | Description |
|------------|----------|-------------|-------------|
| `payload`  | ✅       | —           | List of drawing commands (see [Payload Element Types](#payload-element-types)) |
| `rotate`   | ❌       | `0`         | Label rotation: `0`, `90`, `180`, `270` |
| `width`    | ✅       | —           | Label width in pixels (10-4096)         |
| `height`   | ✅       | —           | Label height in pixels (10–4096)        |
| `mimetype` | ✅       | `image/png` | Format of the output image              |
| `options`  | ❌       | —           | Key/value options pair (see [Image save options](#image-save-options)) |

#### Image save options

Some image formats allow options to be specified.  For example, if drawing to an
`application/pdf`, you can specify the following option:

```yaml
dpi: [300, 300] # resolution of the document in dots per inch
```

resulting in a proportional reduction of paper size in the output PDF data
(the default if nothing is specified is 72 DPI).

### Drawing graphically

The author is kind enough to provide a [Web-based tool to
generate payloads](https://eigger.github.io/Niimbot_Payload_Editor.html)
for the draw action provided by this integration.  From the YAML output
of the tool, the only parameters you can use in this action are:

* payload
* width
* height
* rotate

You can then use these parameters in your scripts or in the Developer
Tools *Actions* section directly.

### Seeing previews in real-time

An entity named *Last generated image* updates to show the contents
of what you've drawn.  Very useful when you are iterating on a design
using the Developer Tools *Actions* tab — just keep the entity open
on another window and watch the image update as you run the action.

<img src="examples/Live%20preview.png" width="630" alt="Live preview"/>

### Examples

#### Basic usage

```yaml
action: simpleimageraster.draw
data:
  payload:
    - type: text
      value: Hello World!
      font: ppb.ttf
      x: 100
      y: 100
      size: 40
  width: 400
  height: 240
```

#### Example of drawing a barcode and some text

```yaml
action: simpleimageraster.draw
data:
  payload:
    - type: text
      value: Hello World!
      font: ppb.ttf
      x: 100
      y: 100
      size: 40
    - type: barcode
      data: "12345"
      code: "code128"
      x: 100
      y: 100
    - type: icon
      value: account-cowboy-hat
      x: 60
      y: 120
      size: 120
    - type: dlimg
      url: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAMAAAAM7l6QAAAAAXNSR0IB2cksfwAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAAAAZQTFRFAAAA////pdmf3QAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB+oEAgssE5VYOZ4AAABRSURBVCjPrZHBCgAgDELd//90h4IMJMe2TnMPUgvxPQgAJFlsTatHDGDj7ZLnMF97Z4hQNM9g490sVsU6FH2JqjSDjXehmH3zo2SoHjbe6WILMVoC3bdBtPUAAAAASUVORK5CYII=
      x: 10
      y: 10
      xsize: 120
      ysize: 120
      rotate: 0
    - type: qrcode
      data: "qr data"
      eclevel: h  # l, m, q, h - more info in docs https://pypi.org/project/qrcode/
      x: 140
      y: 50
      boxsize: 2
      border: 2
      color: "black"
      bgcolor: "white"
  width: 400
  height: 240
```

#### Script example for multiline text with auto-fit

```yaml
alias: Print label with multiple lines of text
description: >-
  Use this tool to quick-print any label, for example a recipient label for
  mailing a letter.  Give the contents of the label, in multiple lines, in the
  `content` field, for the print to be successful.  The text will resize to fit
  the width, and the height will fit a maximum of five lines.
fields:
  contents:
    selector:
      text:
        multiline: true
    name: Contents
    required: true
    description: >-
      Contents of the label (e.g. the full address of a letter's recipient) each
      part in a separate line.
sequence:
  - action: simpleimageraster.draw
    response_variable: result
    data:
      payload:
        - type: new_multiline
          x: 0
          y: 20
          size: 100  # start with a large font size
          width: 520
          height: 300
          fit: true
          font: rbm.ttf
          value: "{{ contents }}"
          # e.g.
          # value: |-
          #   Max Mustermann
          #   Strassenstraße 33
          #   49418 Mallorca
          #   Spain
      width: 584
      height: 350
```

In `type: new_multiline`, the font `size` starts by default at 20, and
the `spacing` between lines defaults to the font size.  You can, of
course, set your own custom font size and spacing.

If you specify `fit_width: True` or `fit: width` and add the required
specific `width` in pixels, the font `size` and `spacing` will be
iteratively reduced until the longest line in the text `value` you
specified fits the required width.

If you specify `fit_height: True` or `fit: height` and add the required
specific `height` in pixels, the font `size` and `spacing` will be
iteratively reduced until the whole text fits vertically in the supplied
height.

To combine both modes, you can specify `fit: True`.

Of course, if font `size` is left to its default, chances are, only very
large amounts of text will cause shrinkage of the font size to fit. In that
case, pass a large font `size` and it will be shrunk to a fitting size.

Note that the top part of letters in italicized text tends to spill outside
the specified width -- try to make your width slightly narrower in that case.

### Payload Element Examples

> [!TIP]
> All elements support the `visible` field (`true`/`false`) to conditionally show or hide them.

#### text

```yaml
- type: text
  value: "Hello World!"
  x: 10
  y: 10
  size: 40
  font: ppb.ttf
  color: black
  anchor: lt
  align: left
  spacing: 5
  stroke_width: 1
  stroke_fill: white
  max_width: 200
```

If `y` is omitted, the element stacks below the previous element (`y_padding` controls the gap, default `10`).

#### multiline

```yaml
- type: multiline
  value: "Line1;Line2;Line3"
  delimiter: ";"
  x: 10
  start_y: 10
  offset_y: 25
  size: 20
  font: ppb.ttf
  color: black
  anchor: lm
  stroke_width: 0
  stroke_fill: white
```

#### new_multiline

Multiline text with optional auto-fit to width/height (see [Script example for multiline text with auto-fit](#script-example-for-multiline-text-with-auto-fit)).

```yaml
- type: new_multiline
  x: 0
  y: 20
  size: 100
  width: 520
  height: 300
  fit: true
  font: rbm.ttf
  value: |
    Line 1
    Line 2
    Line 3
```

#### line

```yaml
- type: line
  x_start: 0
  x_end: 250
  y_start: 64
  y_end: 64
  fill: black
  width: 2
```

#### rectangle

```yaml
- type: rectangle
  x_start: 5
  y_start: 5
  x_end: 100
  y_end: 60
  fill: black
  outline: black
  width: 2
  radius: 10
  corners: "top_left,top_right"
```

#### rectangle_pattern

```yaml
- type: rectangle_pattern
  x_start: 10
  y_start: 10
  x_size: 20
  y_size: 20
  x_repeat: 5
  y_repeat: 3
  x_offset: 5
  y_offset: 5
  fill: black
  outline: black
  width: 1
  radius: 5
  corners: "all"
```

#### circle

```yaml
- type: circle
  x: 125
  y: 64
  radius: 30
  fill: red
  outline: black
  width: 2
```

#### ellipse

```yaml
- type: ellipse
  x_start: 50
  y_start: 20
  x_end: 200
  y_end: 100
  fill: red
  outline: black
  width: 1
```

#### icon

Uses [Material Design Icons](https://pictogrammers.com/library/mdi/). Icon name with or without `mdi:` prefix.

```yaml
- type: icon
  value: "account-cowboy-hat"
  x: 60
  y: 120
  size: 120
  color: black
  anchor: la
  stroke_width: 0
  stroke_fill: white
```

#### dlimg

Supports **HTTP/HTTPS URLs** and **Base64 data URIs** (`data:image/...;base64,...`). Local file paths are not supported.

```yaml
- type: dlimg
  url: "https://example.com/image.png"
  x: 10
  y: 10
  xsize: 100
  ysize: 100
  rotate: 0
```

```yaml
- type: dlimg
  url: "data:image/png;base64,iVBORw0KGgo..."
  x: 10
  y: 10
  xsize: 50
  ysize: 50
```

#### qrcode

```yaml
- type: qrcode
  data: "https://www.home-assistant.io"
  x: 140
  y: 10
  boxsize: 2
  border: 1
  color: black
  bgcolor: white
  eclevel: h
```

`eclevel`: `l`, `m`, `q`, `h` (see [qrcode](https://pypi.org/project/qrcode/)).

#### datamatrix

```yaml
- type: datamatrix
  data: "datamatrix data"
  x: 10
  y: 10
  boxsize: 2
  color: "black"
  bgcolor: "white"
```

#### barcode

```yaml
- type: barcode
  data: "123456789012"
  x: 10
  y: 80
  code: code128
  color: black
  bgcolor: white
  module_width: 0.2
  module_height: 7
  quiet_zone: 6.5
  font_size: 5
  text_distance: 5.0
  write_text: true
```

#### diagram

```yaml
- type: diagram
  x: 0
  y: 0
  width: 250
  height: 128
  margin: 20
  font: ppb.ttf
  bars:
    values: "Mon,10;Tue,25;Wed,15;Thu,30;Fri,20"
    color: black
    margin: 10
    legend_size: 10
    legend_color: black
```

#### plot

Reads entity history from **Home Assistant Recorder**.

```yaml
- type: plot
  data:
    - entity: sensor.temperature
      color: black
      width: 2
  duration: 86400
  x_start: 30
  y_start: 10
  x_end: 290
  y_end: 120
  size: 10
  font: ppb.ttf
  low: 15
  high: 35
  ylegend:
    width: -1
    color: black
    position: left
  yaxis:
    width: 1
    color: black
    tick_width: 2
    tick_every: 5
    grid: 5
    grid_color: black
  debug: false
```

#### progress_bar

```yaml
- type: progress_bar
  x_start: 10
  y_start: 100
  x_end: 240
  y_end: 120
  progress: 75
  direction: right
  background: white
  fill: red
  outline: black
  width: 1
  show_percentage: true
```

### Payload Element Types

> [!TIP]
> All elements support the `visible` field (`true`/`false`, default: `true`) to conditionally show or hide them.

| **Type**              | **Required Fields** | **Optional Fields** | **Description** |
| --------------------- | ------------------- | ------------------- | ---------------- |
| **text**              | `x`, `value`        | `y`, `size`(20), `font`(ppb.ttf), `color`(black), `anchor`(lt), `align`(left), `spacing`(5), `stroke_width`(0), `stroke_fill`(white), `max_width`, `y_padding`(10) | Text. Auto-stacks if `y` omitted. |
| **multiline**         | `x`, `value`, `offset_y` | `start_y`, `delimiter`, `size`(20), `font`, `color`(black), `anchor`(lm), `stroke_width`, `stroke_fill`, `y_padding`(10) | Lines split by delimiter. |
| **new_multiline**     | `x`, `y`, `value`   | `size`(20), `spacing`, `width`, `height`, `fit` / `fit_width` / `fit_height`, `font`, `color`, `anchor`(la), `align`, `stroke_width`, `stroke_fill` | Multiline with optional auto-fit. |
| **line**              | `x_start`, `x_end`  | `y_start`, `y_end`, `fill`(black), `width`(1), `y_padding`(0) | Straight line. |
| **rectangle**         | `x_start`, `x_end`, `y_start`, `y_end` | `fill`, `outline`(black), `width`(1), `radius`(0), `corners`(all) | Rectangle, optional rounded corners. |
| **rectangle_pattern** | `x_start`, `y_start`, `x_size`, `y_size`, `x_repeat`, `y_repeat`, `x_offset`, `y_offset` | `fill`, `outline`, `width`, `radius`, `corners` | Grid of rectangles. |
| **circle**            | `x`, `y`, `radius`  | `fill`, `outline`(black), `width`(1) | Circle. |
| **ellipse**           | `x_start`, `x_end`, `y_start`, `y_end` | `fill`, `outline`, `width`(1) | Ellipse. |
| **icon**              | `x`, `y`, `value`, `size` | `color`/`fill`(black), `anchor`(la), `stroke_width`, `stroke_fill` | [Material Design Icons](https://pictogrammers.com/library/mdi/). |
| **dlimg**             | `x`, `y`, `url`, `xsize`, `ysize` | `rotate`(0) | Image from URL or Base64 data URI. |
| **qrcode**            | `x`, `y`, `data`    | `color`(black), `bgcolor`(white), `border`(1), `boxsize`(2), `eclevel`(h) | QR code. |
| **datamatrix**        | `x`, `y`, `data`    | `color`(black), `bgcolor`(white), `boxsize`(2) | DataMatrix code. |
| **barcode**           | `x`, `y`, `data`    | `code`(code128), `color`, `bgcolor`, `module_width`, `module_height`, `quiet_zone`, `font_size`, `text_distance`, `write_text` | Barcode. |
| **diagram**           | `x`, `y`, `height`  | `width`, `margin`(20), `font`, `bars` | Bar chart. |
| **plot**              | `data`([{`entity`}]) | `duration`(86400), `x_start`, `y_start`, `x_end`, `y_end`, `size`, `font`, `low`, `high`, `ylegend`, `yaxis`, `debug` | Time-series from Recorder. |
| **progress_bar**      | `x_start`, `x_end`, `y_start`, `y_end`, `progress` | `direction`(right), `background`, `fill`, `outline`, `width`, `show_percentage` | Progress bar. |

Note that dimensional units are all given in pixels.  When rendering to PNG or JPEG,
there is no inherent resolution, but when rendering to PDF, the default resolution
will be 72 DPI — leading to a blocky / low-res look if printed.  Use the `options`
feature to change the DPI when rendering to PDF, and use a larger canvas (width / height)
as well as larger dimensions in your elements, to accomodate for the fact that
a higher-resolution PDF will naturally result in smaller printed elements.

## Tools

### [Niimbot Payload Layout Editor](https://eigger.github.io/Niimbot_Payload_Editor.html)

Design label layouts in your browser with drag-and-drop, then copy the generated YAML.
Replace `niimbot.print` with `simpleimageraster.draw` in the resulting YAML, then
delete the `target:` section.  Don't forget to add a `response_variable` to get the results.

## Custom Fonts

* [OpenEPaperLink – supported types (font locations)](https://github.com/OpenEPaperLink/Home_Assistant_Integration/blob/main/docs/drawcustom/supported_types.md#font-locations)
* [OpenEPaperLink – font commit reference](https://github.com/OpenEPaperLink/Home_Assistant_Integration/commit/4817d7d7b2138c31e3744a5f998751a17106037d)

Place `.ttf` files in the integration folder or in `www/fonts` and reference by name (e.g. `ppb.ttf`, `rbm.ttf`).

## References

- [OpenEPaperLink](https://github.com/OpenEPaperLink/Home_Assistant_Integration.git)
