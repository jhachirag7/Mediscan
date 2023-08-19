from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np


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
        price = soup.find("span", attrs={'class':'a-price aok-align-center reinventPricePriceToPayMargin priceToPay'}).find("span", attrs={"class": "a-offscreen"}).string.strip()

    except AttributeError:
        price = ""

    return price


def get_imglink(soup):
    try:
        link=soup.find("img",attrs={'id':'landingImage'})
        link=link.get('src')
    except:
        link=""
    return link

def amzscrap(URL,HEADERS):
    webpage = requests.get(URL, headers=HEADERS)

        # Soup Object containing all data
    soup = BeautifulSoup(webpage.text, "html.parser")

    # Fetch links as List of Tag Objects
    links = soup.find_all("a", attrs={'class':'a-link-normal s-no-outline'})

    # Store the links
    links_list = []

    # Loop for extracting links from Tag Objects
    for link in links:
            links_list.append(link.get('href'))
            
            if len(links_list)>=2:
                break

    d = {"title":[], "price":[],'links':[],'product':[]}

    # Loop for extracting product details from each link 
    for link in links_list:
        try:

            plk="https://www.amazon.in" + link

            new_webpage = requests.get("https://www.amazon.in" + link, headers=HEADERS)

            new_soup = BeautifulSoup(new_webpage.text, "html.parser")

            # Function calls to display all necessary product information
            title =get_title(new_soup)
            price=get_price(new_soup)
            lk=get_imglink(new_soup)
            if title=="":
                continue
            if price=="":
                continue
            d['title'].append(title)
            d['price'].append(price)
            d['links'].append(lk)
            d['product'].append(plk)
        except:
            continue
    amazon_df = pd.DataFrame.from_dict(d)
    amazon_df['title'].replace('', np.nan, inplace=True)
    amazon_df = amazon_df.dropna(subset=['title'])
    return amazon_df