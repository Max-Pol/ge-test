class WeatherScraperException(Exception):
    """Base exception class for weather scraper errors."""

    pass


class InvalidLoginCredentials(WeatherScraperException):
    """Raised when login credentials are invalid."""

    pass


class WeatherScraperRequestError(WeatherScraperException):
    """Raised when there is an error with the weather.com API request."""

    pass
