from unittest.mock import Mock, patch

import pytest
from openai import OpenAI

from app.chat.chat import (
    AskResponse,
    WeatherAgent,
    WeatherAgentError,
    WeatherData,
    build_weather_context,
)

# Test data
SAMPLE_WEATHER_DATA = [
    WeatherData(city="London", weather_condition="rainy", temperature=15.5),
    WeatherData(city="Paris", weather_condition="sunny", temperature=22.0),
    WeatherData(city="Berlin", weather_condition="cloudy", temperature=18.0),
]


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    with patch("app.chat.chat.OpenAI") as mock_client:
        mock_instance = Mock(spec=OpenAI)
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def weather_agent(mock_openai_client):
    """Create a WeatherAgent instance with mocked OpenAI client."""
    return WeatherAgent(openai_api_key="test-key")


def test_weather_agent_initialization():
    """Test WeatherAgent initialization."""
    agent = WeatherAgent(openai_api_key="test-key")
    assert isinstance(agent.client, OpenAI)


def test_build_weather_context():
    """Test the build_weather_context helper function."""
    context = build_weather_context(SAMPLE_WEATHER_DATA)
    expected = (
        "- London: rainy, 15.5°C\n- Paris: sunny, 22.0°C\n- Berlin: cloudy, 18.0°C"
    )
    assert context == expected


def test_build_weather_context_empty_list():
    """Test build_weather_context with empty input."""
    assert build_weather_context([]) == ""


def test_summarize_success(weather_agent, mock_openai_client):
    """Test successful weather summary generation."""
    mock_response = Mock()
    mock_response.output = [
        Mock(content=[Mock(text="It's a mixed bag of weather across Europe.")])
    ]
    mock_openai_client.responses.create.return_value = mock_response

    result = weather_agent.summarize(SAMPLE_WEATHER_DATA)

    assert result == "It's a mixed bag of weather across Europe."
    mock_openai_client.responses.create.assert_called_once()


def test_summarize_empty_input(weather_agent):
    """Test summarize with empty input."""
    result = weather_agent.summarize([])
    assert result == "No weather data available to summarize."


def test_summarize_api_error(weather_agent, mock_openai_client):
    """Test summarize when API call fails."""
    mock_openai_client.responses.create.side_effect = Exception("API Error")

    with pytest.raises(WeatherAgentError) as exc_info:
        weather_agent.summarize(SAMPLE_WEATHER_DATA)

    assert "Failed to generate weather summary" in str(exc_info.value)


def test_ask_success(weather_agent, mock_openai_client):
    """Test successful weather question answering."""
    mock_response = Mock()
    mock_response.output_parsed = AskResponse(
        answer="London is rainy at 15.5°C", matching_cities=["London"]
    )
    mock_openai_client.responses.parse.return_value = mock_response

    result = weather_agent.ask(
        "What's the weather like in London?", SAMPLE_WEATHER_DATA
    )

    assert isinstance(result, AskResponse)
    assert result.answer == "London is rainy at 15.5°C"
    assert result.matching_cities == ["London"]
    mock_openai_client.responses.parse.assert_called_once()


def test_ask_empty_input(weather_agent):
    """Test ask with empty input."""
    result = weather_agent.ask("What's the weather like?", [])

    assert isinstance(result, AskResponse)
    assert result.answer == "No weather data available to answer the question."
    assert result.matching_cities == []


def test_ask_api_error(weather_agent, mock_openai_client):
    """Test ask when API call fails."""
    mock_openai_client.responses.parse.side_effect = Exception("API Error")

    with pytest.raises(WeatherAgentError) as exc_info:
        weather_agent.ask("What's the weather like?", SAMPLE_WEATHER_DATA)

    assert "Failed to generate weather response" in str(exc_info.value)
