DOMAIN = "windfinder"
CONF_LOCATION = "location"
FORECAST_URL = "https://www.windfinder.com/forecast/{}"
SUPERFORECAST_URL = "https://www.windfinder.com/weatherforecast/{}"
PLATFORMS = ["sensor", "button"]

CONF_REFRESH_INTERVAL = "refresh_interval"
DEFAULT_REFRESH_INTERVAL = 30  # minutes

# Mapping of Windfinder's month abbreviations to month numbers
MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}
