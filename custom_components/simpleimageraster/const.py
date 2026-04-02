from homeassistant.config_entries import ConfigEntry
from dataclasses import dataclass
from homeassistant.util.hass_dict import HassKey


@dataclass
class SimpleImageRasterDomainConfig:
    """Class for sharing config data within the IPP printing integration."""

    pass


@dataclass
class SimpleImageRasterData:
    """Class for sharing data within the IPP printing integration."""

    domain_config: SimpleImageRasterDomainConfig


DOMAIN = "simpleimageraster"
type SimpleImageRasterConfigEntry = ConfigEntry[SimpleImageRasterData]
MY_KEY: HassKey[SimpleImageRasterDomainConfig] = HassKey(DOMAIN)
