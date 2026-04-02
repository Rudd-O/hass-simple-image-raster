import sys
import os

sys.path.append(os.path.dirname(__file__))

from imagegen import customimage
import yaml

from homeassistant.core import ServiceCall


data_str = """
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
      value: "Jolly Colombani test beans"
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
        Stock entry note
    - type: qrcode
      x: 5
      "y": 120
      data: "grocy_json_data.grocycode"
      boxsize: 7
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
        500 grams

        Stocked: 2026-01-01

        2027-01-01
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
      value: Note of the lot
  width: 900
  height: 375
"""


def main(output_file: str, format: str):
    data = yaml.safe_load(data_str)
    call = ServiceCall(None, "simpleimageraster", "draw", data=data["data"])  # type: ignore
    result = customimage(call, None)
    with open(output_file, "wb") as o:
        result.save(o, format=format, dpi=(300, 300))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
