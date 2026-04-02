"""Support for viewing last generated image."""

import logging

from homeassistant.components.image import ImageEntity, ImageEntityDescription, Image
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import MY_KEY, EMPTY_PNG, SimpleImageRasterConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: SimpleImageRasterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up image platform for Niimbot."""
    image_coordinator = hass.data[MY_KEY].image_coordinator

    desc = ImageEntityDescription(
        key="last_generated_image",
        name="Last generated image",
    )
    async_add_entities(
        [
            RasterImageEntity(
                hass,
                image_coordinator,
                desc,
                config_entry.entry_id,
            )
        ]
    )


class RasterImageEntity(CoordinatorEntity[DataUpdateCoordinator[Image]], ImageEntity):
    """Base representation of a Niimbot image."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator[Image],
        entity_description: ImageEntityDescription,
        unique_id: str,
    ) -> None:
        """Initialize Image entity."""
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self, hass)
        self.entity_description = entity_description
        self._attr_unique_id = f"{unique_id}_{entity_description.key}"
        self._cached_image = coordinator.data

    @property
    def data(self) -> Image:
        """Return coordinator data for this entity."""
        return self.coordinator.data

    def image(self) -> bytes | None:
        """Return bytes of image."""
        return EMPTY_PNG if not self._cached_image else self._cached_image.content

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Updated image data")
        self._cached_image = self.data
        self._attr_image_last_updated = dt_util.now()
        super()._handle_coordinator_update()
