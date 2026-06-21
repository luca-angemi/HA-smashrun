"""Constants for the Smashrun integration."""

DOMAIN = "smashrun"


NOMINATIN_GEOCODE_BASE_URL = "https://nominatim.openstreetmap.org/reverse?lat="
NOMINATIN_GEOCODE_END_URL = "&format=json&accept-language=en"

SMASHRUN_ACTIVITIES_URL = (
    "https://api.smashrun.com/v1/my/activities/search?count=1&access_token="
)

SMASHRUN_STATS_URL = "https://api.smashrun.com/v1/my/stats?access_token="
SMASHRUN_STATS_BASE = "https://api.smashrun.com/v1/my/stats"
SMASHRUN_ACCESS_TOKEN_QUERY = "?access_token="

SMASHRUN_RUN_BASE = "https://api.smashrun.com/v1/my/activities/"
SMASHRUN_RUN_QUERY = SMASHRUN_ACCESS_TOKEN_QUERY

SMASHRUN_TRAILING_URL = (
    "https://api.smashrun.com/v1/my/activities/search/briefs?fromDate="
)
