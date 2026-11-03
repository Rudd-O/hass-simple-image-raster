"""The simple image raster integration."""

import base64
import io
from pathlib import Path
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

        mime_extensions = {
            "image/png": ".png",
            "image/jpeg": ".jpeg",
            "application/pdf": ".pdf",
        }

        if mimetype not in mime_extensions:
            raise ServiceValidationError(
                "unknown image format %r" % mimetype
            )

        # Validate optional filename before generating the image.
        filename = service.data.get("filename")
        destination = None

        if filename is not None:
            if (
                not isinstance(filename, str)
                or not filename
                or filename in (".", "..")
                or "/" in filename
                or "\\" in filename
            ):
                raise ServiceValidationError(
                    "filename must be a simple filename without a directory"
                )

            expected_extension = mime_extensions[mimetype]

            if Path(filename).suffix != expected_extension:
                raise ServiceValidationError(
                    "filename extension must be %s for %s"
                    % (expected_extension, mimetype)
                )

            media_dirs = hass.config.media_dirs
            if not media_dirs:
                raise ServiceValidationError(
                    "No Home Assistant media directory is configured"
                )

            # Prefer the default local media directory.
            media_dir = media_dirs.get("local") or next(iter(media_dirs.values()))
            destination = Path(media_dir) / filename

        try:
            image = customimage(service, hass)
        except Exception as e:
            raise ServiceValidationError(
                "could not draw image: %s" % e
            ) from e

        options = service.data.get("options", {})
        d = io.BytesIO()

        if mimetype == "image/png":
            image.save(d, format="PNG", **options)
        elif mimetype == "image/jpeg":
            image.save(d, format="JPEG", **options)
        elif mimetype == "application/pdf":
            image.save(d, format="PDF", **options)

        d.flush()
        d.seek(0)
        read = d.read()

        # Save the generated image if filename was specified.
        if destination is not None:
            try:
                await hass.async_add_executor_job(
                    destination.write_bytes, read
                )
            except OSError as e:
                raise ServiceValidationError(
                    "could not save image to %s: %s" % (destination, e)
                ) from e

        encoded = base64.b64encode(read).decode("ascii")

        # Submit preview to the coordinator as PNG.
        d.seek(0)
        d.truncate(0)
        image.save(d, format="PNG")
        d.flush()
        d.seek(0)

        image_coordinator.async_set_updated_data(
            Image(content_type="image/png", content=d.read())
        )

        response = {
            "data": encoded,
            "mimetype": mimetype,
            "encoding": "base64",
        }

        if destination is not None:
            response["path"] = str(destination)

        return {"image": response}

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
