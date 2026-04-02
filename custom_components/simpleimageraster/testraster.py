import sys
import os

sys.path.append(os.path.dirname(__file__))

from imagegen import customimage
import yaml

from homeassistant.core import ServiceCall


data_str = """
data:
  payload:
    - type: circle
      x: 187
      y: 115
      radius: 75
    - type: text
      x: 20
      y: 20
      value: Text
      size: 100
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
