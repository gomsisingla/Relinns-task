import requests
from bs4 import BeautifulSoup
import csv
import openai
import pandas as pd
import numpy as np
import textwrap

# Set up OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'


# Function to extract Product Title
def get_title(soup):

    try:
        # Outer Tag Object
        title = soup.find("span", attrs={"id":'productTitle'})
        
        # Inner NavigatableString Object
        title_value = title.text

        # Title as a string value
        title_string = title_value.strip()

    except AttributeError:
        title_string = ""

    return title_string

# Function to extract Product Price
def get_price(soup):

    try:
        price = soup.find("span", attrs={'id':'priceblock_ourprice'}).string.strip()

    except AttributeError:

        try:
            # If there is some deal price
            price = soup.find("span", attrs={'id':'priceblock_dealprice'}).string.strip()

        except:
            price = ""

    return price

# Function to extract Product Rating
def get_rating(soup):

    try:
        rating = soup.find("i", attrs={'class':'a-icon a-icon-star a-star-4-5'}).string.strip()
    
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class':'a-icon-alt'}).string.strip()
        except:
            rating = ""	

    return rating

# Function to extract Number of User Reviews
def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id':'acrCustomerReviewText'}).string.strip()

    except AttributeError:
        review_count = ""	

    return review_count

# Function to extract Availability Status
def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id':'availability'})
        available = available.find("span").string.strip()

    except AttributeError:
        available = "Not Available"	

    return available

def extract_relevant_data(text):
    # Add your text processing logic here
    # For example, you might want to clean or analyze the text
    processed_text = text.upper()  # Placeholder processing, replace with your logic
    return processed_text[:100]  # Limit to the first 100 words

def process_csv(csv_file_path):
    relevant_data = []

    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            text_column = row.get('text', '')  # Assuming 'text' is the column containing the text
            processed_text = extract_relevant_data(text_column)

            # Store the processed text in relevant_data list
            relevant_data.append(processed_text)

    return relevant_data
    
# Function to fetch website content
def get_website_content():
    csv_file_path = 'amazon_data.csv'  # Replace with the path to your CSV file
    relevant_data = process_csv(csv_file_path)
    return relevant_data

# Function to interact with ChatGPT API
def chat_with_gpt(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Main function
def main():
    # Website URL to scrape
        # add your user agent 
    HEADERS = ({'User-Agent':'', 'Accept-Language': 'en-US, en;q=0.5'})

    # The webpage URL
    URL = "https://www.amazon.com/s?k=playstation+4&ref=nb_sb_noss_2"

    # HTTP Request
    webpage = requests.get(URL, headers=HEADERS)

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "html.parser")

    # Fetch links as List of Tag Objects
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})

    # Store the links
    links_list = []

    # Loop for extracting links from Tag Objects
    for link in links:
            links_list.append(link.get('href'))

    d = {"title":[], "price":[], "rating":[], "reviews":[],"availability":[]}
    
    # Loop for extracting product details from each link 
    for link in links_list:
        new_webpage = requests.get("https://www.amazon.com" + link, headers=HEADERS)

        new_soup = BeautifulSoup(new_webpage.content, "html.parser")

        # Function calls to display all necessary product information
        d['title'].append(get_title(new_soup))
        d['price'].append(get_price(new_soup))
        d['rating'].append(get_rating(new_soup))
        d['reviews'].append(get_review_count(new_soup))
        d['availability'].append(get_availability(new_soup))

    
    amazon_df = pd.DataFrame.from_dict(d)
    amazon_df['title'].replace('', np.nan, inplace=True)
    amazon_df = amazon_df.dropna(subset=['title'])
    amazon_df.to_csv("amazon_data.csv", header=True, index=False)
    
    # Step 2: Extracting data
    website_data = get_website_content()
    
    # Step 3: Processing data
    processed_data = f"Data from the website: {website_data}"
    
    # Step 4: Implementing the chatbot
    print("Chatbot: Hello! I'm your website-interacting chatbot. Ask me anything.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            print("Chatbot: Goodbye!")
            break
        
        chatbot_prompt = f"User: {user_input}\nWebsite Data: {processed_data}\nChatGPT:"
        chatbot_response = chat_with_gpt(chatbot_prompt)
        
        # Step 5: Console demonstration
        print(f"Chatbot: {chatbot_response}")

if __name__ == "__main__":
    main()

