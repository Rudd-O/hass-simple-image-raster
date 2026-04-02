# Grocy label printing

This example shows how to integrate Grocy label printing with Home Assistant
(specifically labels for Grocy lots, although it could be extended for other
types of Grocycode).

## Assumptions

It assumes you have your Home Assistant running at IP address 192.168.1.45,
and you have a DYMO LabelWriter 550 shared somewhere using CUPS,
at IP address 192.168.1.69, loaded with the large address label format
(3.5 inches x 1.4 inches).

Configuring this printer to be shared on the network is beyond the scope of
this guide, but:

1. Most any IPP printer will work, so if your printer is compatible with
   IPP, you're golden.
2. The LPrint project produces [a printer application](https://www.msweet.org/lprint/lprint.html)
   for DYMO printers that should work fine to drive them (via USB or Ethernet).
3. At least up until Fedora 43, a CUPS optional package named `dymo-cups-drivers-lw5xx`
   drives those printers fine.  Install the printer via CUPS, set up your label
   size correctly and set quality to *graphics*, then ensure a test page works,
   and this should work too.
4. Conceivably, a CUPS add-on for Home Assistant could enable your printer
   to work via USB just fine.
5. If you can [get a NIIMBOT printer to work with Home Assistant](https://github.com/eigger/hass-niimbot)
   that might be easier, but do note that NIIMBOT printers are not made to
   stay on 24/7, unlike commercial label printers, and can be flaky;
   I myself started with a NIIMBOT B21 Pro, and I have sold it since.

## How this works

Step by step:

1. You request Grocy print a stock entry Grocycode label.
2. Grocy contacts Home Assistant via a Webhook-triggered automation,
   sending it the Grocycode data.
3. Home Assistant launches the automation and runs a script, relaying
   the Grocyode data.
4. The script receives the data from Grocycode, and formats a label
   using the *Simple image raster* integration as PDF, then sends the
   PDF data to CUPS (or a printer) to be printed.
5. CUPS (or the printer) spools and prints the PDF.
6. You receive sticker.

All of this takes mere seconds.

## Add the IPP printer to Home Assistant

Go to *Devices & services* in the settings of Home Assistant, then click
*Add integration*.  Select *Internet Printing Protocol* and enter the
IP address of your CUPS server / printer in the box that appears
(in our example, it is 192.168.1.45).  In the *Relative path to the
printer* box, add the printer path (in CUPS it would be something
like `/printers/DYMO_LabelWriter_550_Turbo` but in most regular
printers it tends to be simply the `/ipp/print` default).

Submit the form, and verify that a new IPP device was added
successfully.

## Install the Simple image raster and IPP printing integrations via HACS

Add to HACS (as integration type) the following two URLs:

* https://github.com/Rudd-O/homeassistant-ipp-printing
* https://github.com/Rudd-O/hass-simple-image-raster

Install the *IPP printing* and the *Simple image raster* integrations.

Restart Home Assistant.

Go to *Devices & services* in the settings of Home Assistant, then click
*Add integration*.  Add the integration named *IPP printing*, and confirm.
Then add the integration named *Simple image raster* and confirm.

You are ready for the sweet part of the journey.

## Home Assistant script

Create a script and save it as *Print Grocy label*.  Here is the script's YAML code:

```yaml
fields:
  grocy_json_data:
    selector:
      object: {}
    name: Grocy JSON data
    required: true
alias: Print Grocy label
description: ""
sequence:
  - action: logbook.log
    metadata: {}
    data:
      name: Grocy webhook
      message: >-
        was asked to print stock entry {{ grocy_json_data.grocycode }} for {{
        grocy_json_data.stock_entry.amount }} {{
              grocy_json_data.details.quantity_unit_stock.name_plural }} of {{ grocy_json_data.product }} {{ grocy_json_data.stock_entry | default("(No stock entry)") }} 
      entity_id: script.print_grocy_label
  - if:
      - condition: template
        value_template: >-
          {{ "stock_entry" in grocy_json_data and "details" in grocy_json_data
          }}
    then:
      - action: simpleimageraster.draw
        metadata: {}
        data:
          payload:
            - type: new_multiline
              x: 10
              "y": 10
              size: 100
              spacing: 50
              width: 880
              height: 50
              fit: true
              font: rbm.ttf
              value: "{{ grocy_json_data.product }}"
            - type: new_multiline
              x: 10
              "y": 60
              size: 100
              spacing: 50
              width: 880
              height: 50
              fit: true
              font: rbm.ttf
              value: >-
                {% if grocy_json_data.stock_entry.note -%}↳ {{
                grocy_json_data.stock_entry.note }}{% endif -%}
            - type: qrcode
              x: 5
              "y": 120
              boxsize: 7
              data: "{{ grocy_json_data.grocycode }}"
            - type: new_multiline
              x: 260
              "y": 120
              size: 100
              spacing: 30
              width: 630
              height: 150
              fit: true
              font: rbm.ttf
              value: >-
                {{ grocy_json_data.stock_entry.amount }} {{
                grocy_json_data.details.quantity_unit_stock.name_plural }}

                Stocked: {{ grocy_json_data.stock_entry.purchased_date }}

                {{ grocy_json_data.due_date }}
            - type: new_multiline
              x: 260
              "y": 360
              anchor: ls
              size: 100
              spacing: 50
              width: 630
              height: 30
              fit: true
              font: rbm.ttf
              value: "{{ grocy_json_data.grocycode }}"
          width: 900
          height: 375
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
    else:
      - action: logbook.log
        metadata: {}
        data:
          name: Grocy webhook
          message: >-
            was asked to print but doesn't know how to print {{ grocy_json_data
            }}
          entity_id: script.print_grocy_label
```

Go back to the UI mode, and expand the *IPP printing 'Print'* action.
Click on *Add target* then *Device*, and select your IPP printer.

## Home Assistant automation

Create an automation named *Print Grocycode label when Grocy requests it*.

Add a *Webhook* trigger, then copy the Webhook ID and save it somewhere
(you'll need it soon).

For the actions, use the following YAML code (edit the automation as YAML):

```yaml
# ... alias: Print Grocycode label when Grocy requests it
# ... description: ""
# ... triggers:
# ...   - trigger: webhook
# ...     allowed_methods:
# ...       - POST
# ...       - PUT
# ...     local_only: true
# ...     webhook_id: "-......"
# ... conditions: []
actions:
  - action: script.print_grocy_label
    metadata: {}
    data:
      grocy_json_data: "{{ trigger.json }}"
mode: single
```

Save the automation.

## Grocy configuration (`config.php`)

Add the following lines to your Grocy configuration file (`config.php`) to
enable the label printer webhook. Replace `LABEL_PRINTER_WEBHOOK` with
your Home Assistant webhook URL (including the Webhook ID that Home Assistant
generated in the prior step).

```php
Setting('LABEL_PRINTER_WEBHOOK', 'http://192.168.1.45:8123/api/webhook/<paste Webhook ID here>');
Setting('FEATURE_FLAG_LABEL_PRINTER', true);
```

## Finished!

Now, every time Grocy wants to print a stock entry Grocycode,
you'll see a new label being printed out in a matter of seconds.

## Sample label

<img src="Grocy%20label.jpg" width="630" alt="Grocy Example"/>
