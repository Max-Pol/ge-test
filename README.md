# GE Test

## Requirements
- Docker (tested with Docker 28.1.1, Compose v2.35)


## Getting Started
Getting the project up and running is simple! Just follow these steps:

1. Start the application:
```bash
docker compose up
```

2. Once running, you can:
   - Verify everything is working by visiting the health check endpoint: http://0.0.0.0:8000/api/v1/health
   - Explore the API documentation and try out endpoints interactively at: http://0.0.0.0:8000/docs

Want to quickly test the API? You have two options:
- Run the ready-to-use onboard script: `./scripts/onboard_script.sh`
- Or experiment with individual curl commands from the onboard script

## Project Structure
```sh
├──app                   # Python FastAPI app code
|    ├── api                # API routes and endpoints
|    |    ├── chat              # Chat endpoints for weather queries and summaries
|    |    ├── cities            # Favorite City management with weather data
|    |    ├── health            # Health check endpoint
|    |    └── users             # User authentication and management endpoints
|    ├── chat               # Chat functionality using OpenAI GPT
|    |    ├── chat.py           # WeatherAgent implementation for weather queries
|    |    └── prompts.py        # System prompts for weather-related conversations
|    ├── core               # Core application functionality
|    |    ├── auth.py           # Authentication and JWT token management
|    |    └── config.py         # Application settings and configuration
|    ├── weather            # Weather data handling
|    |    ├── city.py           # City information and weather data retrieval
|    |    ├── exceptions.py     # Custom weather-related exceptions
|    |    └── scraper.py        # Weather.com API integration and scraping
|    ├── main.py            # FastAPI application entry point
|    ├── models.py          # Pydantic & DB models for data validation
|    └── repository.py      # Database operations
├──scripts               # Utility scripts
|    ├── init-db.py         # Database initialization script
|    └── test_script.sh     # API testing script
├──tests                 # Project tests
|
```

## Development
#### Live-Reloading
- To launch the app with live reloading, use [Compose Watch](https://docs.docker.com/compose/how-tos/file-watch/):
```bash
docker compose up --watch
```

#### Database initialization
As I did not implement migrations, if you want to initialize the database just run:
```
python ./scripts/init-db.py
```
#### Run tests
```
/scripts/test.sh
```

## Improvements
### Code Quality
- Add more tests...
- Improve Error Handling
- CI/CD
- Pre-commit Linters 
- Add proper migrations using Alembic
- ...

### Scaling to 100,000 Cities

The current implementation faces challenges when scaling to handle 100,000 cities:

- Modern LLMs, despite their large context windows, would struggle with the extensive weather data context
- This approach would be inefficient in terms of:
  - Cost optimization
  - Performance
  - Risk of context window limitations ("lost in the middle" effect)

Some Solutions:
1. Implement a Vector Database with RAG (Retrieval-Augmented Generation):
   - Store weather data in a vector database
   - Use semantic search to retrieve the most relevant weather information for each query
   - This enables efficient context retrieval and reduces token usage

2. Leverage LLMs for Smart City Selection:
   - Use LLMs to generate optimized search queries
   - Improve city selection accuracy and relevance
   - Reduce the amount of data needed for each request
