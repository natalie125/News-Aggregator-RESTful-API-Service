import json

import requests

CATEGORY_CHOICES = [
    ('pol', 'Politics'),
    ('art', 'Art'),
    ('tech', 'Technology'),
    ('trivia', 'Trivia'),
]

REGION_CHOICES = [
    ('uk', 'UK'),
    ('eu', 'European Union'),
    ('w', 'World'),
]


def login(url):
    print(f"Logging in to {url}")
    username = input("Username: ")
    password = input("Password: ")
    login_endpoint = f"{url}/api/login"
    data = {"username": username, "password": password}

    response = requests.post(login_endpoint, data=data)

    if response.ok:
        print("Login successful!")
        print(response.text)
        # Extract and return the token from the response
        token = response.text.split('token is ')[1]  # Simplified extraction based on given format
        return token
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None


def logout(url):
    """Log out from the news service."""
    if url is None:
        print("You are not logged in to any service.")
        return
    print(f"Logging out from {url}")
    logout_endpoint = f"{url}/api/logout"
    response = requests.post(logout_endpoint)
    if response.ok:
        print("Logout successful!")
        print(response.text)
    else:
        print(f"Logout failed: {response.status_code}")
        print(response.text)


def post_story(url, token):
    if url is None:
        print("Please log in before posting a story.")
        return

    print("Enter story details:")
    headline = input("Headline: ")

    print("Choose a category:")
    for i, (code, name) in enumerate(CATEGORY_CHOICES, start=1):
        print(f"{i}. {name}")
    category_index = int(input("Choose a number for category: ")) - 1
    category = CATEGORY_CHOICES[category_index][0]

    print("Choose a region:")
    for i, (code, name) in enumerate(REGION_CHOICES, start=1):
        print(f"{i}. {name}")
    region_index = int(input("Choose a number for region: ")) - 1
    region = REGION_CHOICES[region_index][0]

    details = input("Details: ")

    story_data = {
        "headline": headline,
        "category": category,
        "region": region,
        "details": details
    }

    post_endpoint = f"{url}/api/stories"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {token}'  # Include the token in the request headers
    }
    response = requests.post(post_endpoint, headers=headers, data=json.dumps(story_data))

    if response.status_code == 201:
        print("Story posted successfully.")
    else:
        print(f"Failed to post story: {response.status_code}")
        print(response.text)


def fetch_news(url, category, region, date):
    if not url:
        print("URL is required to fetch news.")
        return

    # Construct the URL based on the provided agency code
    url = f"{url}/api/stories"

    # Construct query parameters
    params = {'story_cat': category, 'story_region': region, 'story_date': date}

    response = requests.get(url, params=params)
    if response.ok:
        response_json = response.json()
        if "stories" in response_json:  # Checking if 'stories' key exists
            news_stories = response_json["stories"]
            if news_stories:  # Check if the list is not empty
                # print("News Stories:")
                for story in news_stories:
                    # Ensure each 'story' is a dictionary before attempting to access its data
                    if isinstance(story, dict):
                        print("Key:", story.get("key", "N/A"))
                        print("Headline:", story.get("headline", "N/A"))
                        print("Category:", story.get("story_cat", "N/A"))
                        print("Region:", story.get("story_region", "N/A"))
                        print("Author:", story.get("author", "N/A"))
                        print("Date:", story.get("story_date", "N/A"))
                        print("Details:", story.get("story_details", "N/A"))
                        print("---" * 10)  # Separator for readability
            else:
                print("No news stories found matching the criteria.")
        else:
            print("Unexpected response format. 'stories' key not found.")
    else:
        print(f"Failed to fetch news stories: {response.status_code}")
        print(response.text)



def list_news_services():
    directory_url = "http://newssites.pythonanywhere.com/api/directory/"
    response = requests.get(directory_url)
    if response.ok:
        news_services = response.json()
        print("List of News Services:")
        for service in news_services:
            print(
                f"- Agency Name: {service['agency_name']}, URL: {service['url']}, Agency Code: {service['agency_code']}")
    else:
        print(f"Failed to retrieve news services list: {response.status_code}")
        print(response.text)


def delete_story(url, token, story_key):
    if url is None or token is None:
        print("Please log in before attempting to delete a story.")
        return

    delete_endpoint = f"{url}/api/stories/{story_key}/"  # Assuming the endpoint follows this pattern
    headers = {
        'Authorization': f'Token {token}'  # Use the authenticated user's token
    }
    response = requests.delete(delete_endpoint, headers=headers)

    if response.status_code == 200:
        print("Story deleted successfully.")
    else:
        print(f"Failed to delete story: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    url = None
    token = None  # Variable to hold the authentication token
    while True:
        full_command = input("Enter command ('login <url>', 'logout', 'post', 'news -id= -cat= -reg= -date=', 'list', 'delete <story_key>', or 'exit'): ").strip()
        command_parts = full_command.split()
        command = command_parts[0]

        if command == "login" and len(command_parts) == 2:
            url = command_parts[1]
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            token = login(url)  # Save the token from login
        elif command == "logout":
            logout(url)
            url = None
            token = None  # Clear the token on logout
        elif command == "post":
            if token:
                post_story(url, token)  # Pass the token to the post function
            else:
                print("Please log in first.")
        elif command == "news":
            id, cat, reg, date = None, "*", "*", "*"
            for part in command_parts[1:]:  # Skip 'news' command itself
                if "=" in part:
                    key, value = part.split("=", 1)  # Split on first '='
                    if key == "-id":
                        id = value
                    elif key == "-cat":
                        cat = value
                    elif key == "-reg":
                        reg = value
                    elif key == "-date":
                        date = value
            print(f"id: {id}, Category: {cat}, Region: {reg}, Date: {date}")

            # Fetch and list news services to find the URL based on agency_code
            directory_response = requests.get("http://newssites.pythonanywhere.com/api/directory/")
            if directory_response.ok:
                news_services = directory_response.json()
                for service in news_services:
                    # If an ID is specified, fetch news only from the corresponding service
                    if id:
                        if service['agency_code'] == id:
                            print(f"Fetching news from {service['agency_name']}...")
                            fetch_news(service['url'], cat, reg, date)
                            break  # Stop after finding the specified service
                    # If no ID is specified, fetch news from every service
                    else:
                        print(f"Fetching news from {service['agency_name']}...")
                        fetch_news(service['url'], cat, reg, date)
            else:
                print("Failed to retrieve news services list.")
        elif command == "list":
            list_news_services()  # Call the function to list news services
        elif command == "delete" and len(command_parts) == 2:
            story_key = command_parts[1]
            delete_story(url, token, story_key)  # Call the function to delete a story
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Unsupported command or incorrect format.")
