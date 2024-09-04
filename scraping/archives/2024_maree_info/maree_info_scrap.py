import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Function to generate the list of URLs
def generate_urls(start_date, end_date, base_url):
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime("%Y%m%d")
        url = f"{base_url}?d={formatted_date}"
        date_list.append(url)
        current_date += timedelta(days=1)
    return date_list

# Function to fetch content from each URL and parse the table
def fetch_data_and_parse_table(urls):
    # Create a session to persist certain parameters across requests
    session = requests.Session()

    # Set headers to mimic a real browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

    # Optionally set cookies if you have specific ones (e.g., from a previous login)
    session.cookies.update({
        'PHPSESSID': 'eu4rdmc1l4ni1ct3rnbb5doi12',
        'UserAgreement': 'c2bbe24a9764d864425be4a72eacbe0452d78365868c20d03f46e6b05f2572ba1df03c66',
    })

    data = {}
    current_coef = None
    for url in urls:
        try:
            response = session.get(url)
            if response.status_code == 200:
                print(f"Success: {url}")
                # print(response.text)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find the table with id MareeJourDetail_0
                day = soup.find('tr', id='MareeJours_0')
                
                if day:
                    date = url.split('=')[-1]
                    cols = [td.contents for td in day.find_all('td')]
                    cols = [list(filter(lambda tag: tag.name != 'br', tag_list)) for tag_list in cols]
                    transposed_data = list(map(list, zip(*cols)))


                    def parse_height(height_str):
                        # Remove the 'm' at the end and replace ',' with '.'
                        return float(height_str.replace('m', '').replace(',', '.'))

                    def parse_coef(coef_str):
                        # Handle the case where coef is not a number (like '\xa0')
                        return int(coef_str) if coef_str.strip() and coef_str.isdigit() else None

                    def determine_tide(height):
                        if height.name == 'b':
                            return "Haute"
                        else:
                            return "Basse"

                    # Initialize the list of dictionaries
                    result = []

                    
                    # Iterate over the data to transform each list into a dictionary
                    for idx, entry in enumerate(transposed_data):
                        time = entry[0].get_text(strip=True) if isinstance(entry[0], str) else entry[0].text
                        height = parse_height(entry[1]) if isinstance(entry[1], str) else parse_height(entry[1].text)
                        coef = parse_coef(entry[2]) if isinstance(entry[2], str) else parse_coef(entry[2].text)

                        if coef is not None:
                            current_coef = coef
                        elif coef is None and current_coef is not None:
                            coef = current_coef
                        elif coef is None and current_coef is None:
                            nextEntry = transposed_data[idx+1]
                            coef = parse_coef(nextEntry[2]) if isinstance(nextEntry[2], str) else parse_coef(nextEntry[2].text)
                            current_coef = coef


                        tide = determine_tide(entry[1])

                        result.append({
                            'time': time,
                            'height': height,
                            'coef': coef,
                            'tide': tide
                        })
                    data[date] = result
                else:
                    print(f"No table found with id 'MareeJourDetail_0' in {url}")
            else:
                print(f"Failed to retrieve data from {url}, Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
    print(data)
    return data
    

# Main part of the script
if __name__ == "__main__":
    base_url = "https://maree.info/93"
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2024, 12, 31)

    urls = generate_urls(start_date, end_date, base_url)
    data = fetch_data_and_parse_table(urls)
    # Print to file
    with open('scraping/2024_maree_info/maree_info_raw_dict.txt', 'w') as f:
        f.write(str(data))
    
