"""The simple image raster integration."""

import base64
import io

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.const import Platform

from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    SimpleImageRasterConfigEntry,
    MY_KEY,
    SimpleImageRasterData,
    SimpleImageRasterDomainConfig,
)
from .imagegen import customimage

PLATFORMS: list[Platform] = []


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    domain_config = SimpleImageRasterDomainConfig()

    hass.data[MY_KEY] = domain_config

    @callback
    # callback for the draw custom service
    async def genservice(service: ServiceCall) -> ServiceResponse:
        mimetype = service.data.get("mimetype", "image/png")
        if mimetype not in ["image/png", "image/jpeg", "application/pdf"]:
            raise ServiceValidationError("unknown image format %r" % mimetype)

        try:
            image = customimage(service, hass)
        except Exception as e:
            raise ServiceValidationError("could not draw image: %s" % e) from e

        options = service.data.get("options", {})

        d = io.BytesIO()
        if mimetype == "image/png":
            image.save(d, format="PNG", **options)
        elif mimetype == "image/jpeg":
            image.save(d, format="JPEG", **options)
        elif mimetype == "application/pdf":
            image.save(d, format="PDF", **options)
        else:
            assert 0, "not reached with %r" % mimetype
        d.flush()
        d.seek(0)
        read = d.read()
        encoded = base64.b64encode(read).decode("ascii")
        return {"image": {"data": encoded, "mimetype": mimetype, "encoding": "base64"}}

    # register the services
    hass.services.async_register(
        DOMAIN, "draw", genservice, supports_response=SupportsResponse.ONLY
    )

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SimpleImageRasterConfigEntry,
) -> bool:
    """Set up a config entry."""

    domain_config = hass.data[MY_KEY]

    config_entry.runtime_data = SimpleImageRasterData(
        domain_config=domain_config,
    )

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    config_entry: SimpleImageRasterConfigEntry,
) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_remove_entry(
    hass: HomeAssistant,
    config_entry: SimpleImageRasterConfigEntry,
) -> None:
    """Integration removed."""
    pass
