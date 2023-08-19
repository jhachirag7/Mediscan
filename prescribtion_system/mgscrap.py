from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np



def get_title(soup):
    
    try:
        # Outer Tag Object
        title = soup.find("h1", attrs={"class":'DrugHeader__title-content___2ZaPo'})
        
        # Inner NavigatableString Object
        title_value = title.text

        # Title as a string value
        title_string = title_value.strip()

    except:
        title_string = ""

    return title_string

# Function to extract Product Price
def get_price(soup):

    try:
        price = soup.find("div", attrs={'class':'DrugPriceBox__best-price___32JXw'}).text.strip()

    except:
        try:
            price=soup.find("span", attrs={'class':'PriceBoxPlanOption__offer-price___3v9x8 PriceBoxPlanOption__offer-price-cp___2QPU_'}).text.strip()
        except:
            price = ""

    return price






def mgscrap(URL,HEADERS):
    try:
        webpage = requests.get(URL, headers=HEADERS)

        # Soup Object containing all data
        soup = BeautifulSoup(webpage.text, "html.parser")
        links = soup.find_all("a", attrs={'target':'_blank','rel':'noopener'})
        links_list=[]
        for link in links:
                links_list.append(link.get('href'))
                
                if len(links_list)>=5:
                    break
        d = {"title":[], "price":[],'links':[],'product':[]}

        for link in links_list:
            try:
                plk="https://www.1mg.com" + link
                new_webpage = requests.get("https://www.1mg.com" + link, headers=HEADERS)


                new_soup = BeautifulSoup(new_webpage.text, "html.parser")
                title =get_title(new_soup)
                price=get_price(new_soup)
                if title=="":
                    continue
                if price=="":
                    continue
                d['title'].append(title)
                d['price'].append(price)
                d['links'].append("")
                d['product'].append(plk)
            except:
                continue
            
        mg_df = pd.DataFrame.from_dict(d)
        mg_df['title'].replace('', np.nan, inplace=True)
        mg_df = mg_df.dropna(subset=['title'])
        return mg_df

    except:
        df =  {"title":[], "price":[],'links':[],'product':[]}
        mg_df = pd.DataFrame.from_dict(df)
        mg_df['title'].replace('', np.nan, inplace=True)
        mg_df = mg_df.dropna(subset=['title'])
        return mg_df