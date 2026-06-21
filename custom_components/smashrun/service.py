"""Define services for the Smashrun integration."""

from functools import partial

from homeassistant.const import CONF_TOKEN
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.helpers.httpx_client import get_async_client

from .api import get_latest_run_data
from .const import DOMAIN


async def get_latest_run(
    call: ServiceCall, hass: HomeAssistant, token
) -> ServiceResponse:
    """Get run service."""
    client = get_async_client(hass)
    run = await get_latest_run_data(client, token)
    return {"run": run}


@callback
def async_setup_services(hass: HomeAssistant, config_entry) -> None:
    """Set up the services for the Smashrun integration."""
    token = config_entry.data.get(CONF_TOKEN)

    hass.services.async_register(
        DOMAIN,
        "get_latest_run",
        partial(get_latest_run, hass=hass, token=token),
        schema=None,
        supports_response=SupportsResponse.ONLY,
    )
