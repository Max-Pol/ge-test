#!/bin/bash

BASE_URL="http://0.0.0.0:8000/api/v1"
EMAIL="james.bond00007@gmail.com"
PASSWORD='0OhJames!'

# Function to print step header
step() {
    echo -e "\n\n=== Step $1: $2 ==="
    echo "----------------------------------------"
}

# Step 1: Verify the API service is running and healthy
step "1" "Checking API Health"
curl $BASE_URL/health

# Step 2: Create a new user account with email and password
# IMPORTANT NOTE: If you want to be able to scrap weather.com, you need to signup and
# login with the same credentials as the ones you used in weather.com!!!
step "2" "Creating User Account"
curl -H "Content-Type: application/json" $BASE_URL/users/signup --data '{"email":"'"$EMAIL"'","password":"'"$PASSWORD"'"}'

# Step 3: Login to get an access token
step "3" "Logging In"
curl -H "Content-Type: application/x-www-form-urlencoded" $BASE_URL/users/login --data-urlencode "username=$EMAIL" --data-urlencode "password=$PASSWORD"

# Step 4: Store the access token for subsequent API calls
step "4" "Storing Access Token"
TOKEN=$(curl -H "Content-Type: application/x-www-form-urlencoded" $BASE_URL/users/login --data-urlencode "username=$EMAIL" --data-urlencode "password=$PASSWORD" | jq -r '.access_token')
echo "Token stored successfully"

# Step 5: Verify the token works by fetching user profile
step "5" "Verifying Token"
curl $BASE_URL/users/me -H "Authorization: Bearer $TOKEN"

# Step 6: Get list of favorite cities and their current weather
step "6" "Fetching Favorite Cities"
curl $BASE_URL/cities/favorites -H "Authorization: Bearer $TOKEN"

# Step 7: Add new cities to favorites list
step "7" "Adding Favorite Cities"
curl -X POST $BASE_URL/cities/favorites -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"cities": ["London", "Birmingham", "Manchester", "Glasgow", "Leeds"]}'

# Step 8: Get a summary of weather conditions across favorite cities
step "8" "Getting Weather Summary"
curl -X POST $BASE_URL/chat/summary -H "Authorization: Bearer $TOKEN"

# Step 9: Ask a specific weather-related question
step "9" "Asking Weather Question"
curl -X POST $BASE_URL/chat/ask -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"question": "Which cities have sunny weather now so that I can go sunbathing?"}'
