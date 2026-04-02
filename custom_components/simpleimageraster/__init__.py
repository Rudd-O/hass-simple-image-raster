"""The simple image raster integration."""

import base64
import io
import logging

from homeassistant.components.image import Image
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    EMPTY_PNG,
    MY_KEY,
    SimpleImageRasterConfigEntry,
    SimpleImageRasterData,
    SimpleImageRasterDomainConfig,
)
from .imagegen import customimage

PLATFORMS: list[Platform] = [Platform.IMAGE]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    image_coordinator: DataUpdateCoordinator[Image] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
    )
    image_coordinator.async_set_updated_data(
        Image(content_type="image/png", content=EMPTY_PNG)
    )

    domain_config = SimpleImageRasterDomainConfig(image_coordinator=image_coordinator)
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

        # Submit preview to the coordinator.
        d.seek(0)
        d.truncate(0)
        image.save(d, format="PNG")
        d.flush()
        d.seek(0)
        image_coordinator.async_set_updated_data(
            Image(content_type="image/png", content=d.read())
        )

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
