import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.amazon.in'
PAGE_LIMIT = 20

# Function to scrape product details from a page
def scrape_product_details(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    # Find the parent container for each product
    product_containers = soup.find_all('div', class_='s-result-item')

    for container in product_containers:
        product = {}

        # Extract product URL
        url_tag = container.find('a', class_='a-link-normal')
        if url_tag:
            product['Product URL'] = BASE_URL + url_tag['href']
        else:
            product['Product URL'] = ''

        # Extract product name
        name_tag = container.find('span', class_='a-size-medium')
        if name_tag:
            product['Product Name'] = name_tag.text.strip()
        else:
            product['Product Name'] = ''

        # Extract product price
        price_tag = container.find('span', class_='a-price-whole')
        if price_tag:
            product['Product Price'] = price_tag.text.strip()
        else:
            product['Product Price'] = ''

        # Extract product rating
        rating_tag = container.find('span', class_='a-icon-alt')
        if rating_tag:
            product['Rating'] = rating_tag.text.strip().split()[0]
        else:
            product['Rating'] = ''

        # Extract number of reviews
        reviews_tag = container.find('span', class_='a-size-base')
        if reviews_tag:
            product['Number of Reviews'] = reviews_tag.text.strip()
        else:
            product['Number of Reviews'] = ''
        
        # Extract product rating
        ass = container.get('data-asin')
        if ass:
            product['ASIN'] = ass
        else:
            product['ASIN'] = ''

        products.append(product)

    return products

# Function to scrape additional details for a product
def scrape_additional_details(product_url):
    if not product_url:
        return {}

    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_details = {}

    # Extract ASIN
    # asin_tag = soup.find('th', text='ASIN')
    # if asin_tag and asin_tag.find_next_sibling('td'):
    #     product_details['ASIN'] = asin_tag.find_next_sibling('td').text.strip()
    # else:
    #     product_details['ASIN'] = ''

    # Extract product description
    description_tag = soup.find('div', id='productDescription')
    if description_tag:
        product_details['Product Description'] = description_tag.text.strip()
    else:
        product_details['Product Description'] = ''

    # Extract manufacturer
    manufacturer_tag = soup.find('a', id='bylineInfo')
    if manufacturer_tag:
        product_details['Manufacturer'] = manufacturer_tag.text.strip()
    else:
        product_details['Manufacturer'] = ''

    return product_details


# Function to scrape product data
def scrape_product_data():
    all_products = []

    for page in range(1, PAGE_LIMIT + 1):
        page_url = f'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{page}'
        products = scrape_product_details(page_url)
        all_products.extend(products)

    product_data = []

    for product in all_products:
        additional_details = scrape_additional_details(product['Product URL'])
        product_data_item = {**product, **additional_details}
        product_data.append(product_data_item)

    return product_data


# Export product data to a CSV file
def export_to_csv(product_data, file_path):
    if not product_data:
        print('No data to export.')
        return

    keys = product_data[0].keys()

    with open(file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(product_data)

    print(f'Data exported to {file_path}')


# Run the scraper
product_data = scrape_product_data()
export_to_csv(product_data, 'product_data.csv')
