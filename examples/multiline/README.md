# Arbitrary lines of text, printed to your printer

This example script assumes you have a printer or label maker already set up
more or less like [described in the Grocy example](../grocy/README.md).

The format of the printout as shown in the script is adequate for
a large address label — you can instead choose to draw the text
around a different size box, or change the width and the height
to suit your needs.

Create a new script, and switch to the YAML view.  Paste this code.

```yaml
sequence:
  - action: simpleimageraster.draw
    metadata: {}
    data:
      payload:
        - type: new_multiline
          x: 30
          "y": 15
          size: 100
          spacing: 50
          width: 840
          height: 345
          fit: true
          font: rbm.ttf
          value: "{{ contents }}"
      width: 900
      height: 375
      preview: "{{ preview|default(False) }}"
      mimetype: application/pdf
      options:
        dpi:
          - 300
          - 300
    response_variable: image
  - action: ipp_printing.print
    metadata: {}
    data:
      data: "{{ image.image.data }}"
      mimetype: "{{ image.image.mimetype }}"
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
  preview:
    selector:
      boolean: {}
    name: Preview
    description: "If true, doesn't print a label. "
    default: false
    required: false
alias: Print label with multiple lines of text
description: >-
  Use this tool to quick-print any label, for example a recipient label for
  mailing a letter, or whatever the uses asks.  Give the contents of the label,
  in multiple lines of needed, in the `contents` field, for the print to be
  successful.  The text will resize to fit the width, and the height will fit a
  maximum of five lines.
mode: queued
max: 10
```

Switch back to the regular UI view, and in the *IPP Printing 'Print'* action,
select a target, then click *Device*, then select your IPP printer.

Save the script.

Presto!  You can now invoke the script and add whatever lines of text you
want to print.

Optionally, expose your script to your voice assistant, so that
your home LLM can respond appropriately when you say, e.g.,
*Okay, Nabu, print me a label that on the first line says "Hello" and
on the second line says "World"*.  We use this all the time.