"""Entities for the ViCare integration."""

from PyViCare.PyViCareDevice import Device as PyViCareDevice
from PyViCare.PyViCareDeviceConfig import PyViCareDeviceConfig
from PyViCare.PyViCareHeatingDevice import (
    HeatingDeviceWithComponent as PyViCareHeatingDeviceComponent,
)

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class ViCareEntity(Entity):
    """Base class for ViCare entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        unique_id_suffix: str,
        device_serial: str | None,
        device_config: PyViCareDeviceConfig,
        device: PyViCareDevice,
        component: PyViCareHeatingDeviceComponent | None = None,
    ) -> None:
        """Initialize the entity."""
        gateway_serial = device_config.getConfig().serial
        device_id = device_config.getId()
        model = device_config.getModel().replace("_", " ")

        identifier = (
            f"{gateway_serial}_{device_serial.replace('zigbee-', 'zigbee_')}"
            if device_serial is not None
            else f"{gateway_serial}_{device_id}"
        )

        self._api: PyViCareDevice | PyViCareHeatingDeviceComponent = (
            component if component else device
        )
        self._attr_unique_id = f"{identifier}-{unique_id_suffix}"
        if component:
            self._attr_unique_id += f"-{component.id}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            serial_number=device_serial,
            name=model,
            manufacturer="Viessmann",
            model=model,
            configuration_url="https://developer.viessmann.com/",
        )
        
    _attr_operation_modes = list(VICARE_OPERATION_MODES.keys())

  @property
    def operation_mode(self) -> str:
        """Return current operation mode as a user-friendly string."""
        vicare_mode = getattr(self, "_current_mode", None)
        for name, api_mode in OPERATION_MODES.items():
            if vicare_mode == api_mode:
                return name
        return "Unknown"

    @property
    def operation_modes(self) -> list[str]:
        """Return available operation modes."""
        return list(OPERATION_MODES.keys())

    def set_operation_mode(self, mode: str) -> None:
        """Set operation mode ('Off', 'DHW only', or 'DHW and Heating')."""
        vicare_mode = OPERATION_MODES.get(mode)
        if not vicare_mode or vicare_mode not in getattr(self, "_attributes", {}).get("vicare_modes", []):
            raise ValueError(f"Operation mode '{mode}' is not available.")
        self._api.setMode(vicare_mode)
        self._current_mode = vicare_mode
