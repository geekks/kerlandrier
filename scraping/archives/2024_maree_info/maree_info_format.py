import math
import pandas as pd
def create_df():
    with open('scraping/2024_maree_info/maree_info_raw_dict.txt', 'r') as f:
        data = eval(f.read())
        # Convert the dictionary to a list of records with the date key as a new column
        records = []
        for date, entries in data.items():
            for entry in entries:
                entry['date'] = date  # Add the date as a new field
                records.append(entry)

        # Create a DataFrame from the records
        df = pd.DataFrame(records)

        # Reorder columns if needed, for example, placing 'date' as the first column
        df = df[['date', 'time', 'height', 'coef', 'tide']]
        # Save to pickle
        df.to_pickle('scraping/2024_maree_info/maree_info_raw.pkl')

        # Display the DataFrame
        print(df)
        return df

def format_df():
    try:
        df = pd.read_pickle('scraping/2024_maree_info/maree_info_raw.pkl')
    except:
        df = create_df()
    
    # Convert date column to datetime
    df['d'] = df['date']
    df['date'] = pd.to_datetime(df['date'])

    # Replace h by ':' in time column
    df['time'] = df['time'].str.replace('h', ':', regex=False)

   # Create datetime from date and time
    df['datetime_start'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
    df['datetime_end'] = df['datetime_start'] + pd.Timedelta(minutes=1)


    # Add necessary columns to match
    # # title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name
    df['title'] = 'Grande marée (' + df['tide'].astype(str) + ")"
    # tide
    # height
    df['start_date'] = df['datetime_start'].dt.strftime('%Y-%m-%dT%H:%M:%s+0200')
    df['end_date'] = df['datetime_end'].dt.strftime('%Y-%m-%dT%H:%M:%s+0200')
    df['location_uid'] = 95821135
    df['link'] = 'https://www.maree.info/93?d=' + df['d']
    df['img'] = ""
    # cast to int
    df['coef'] = df['coef'].apply(lambda x: int(x) if not math.isnan(x)  else 0)
    df["location_name"] = ""



    print(df.head(2))
    print(df['coef'])

    # Save to pickle
    df.to_pickle('scraping/2024_maree_info/maree_info_format.pkl')
    return df

def format_csv():
    df = pd.read_pickle('scraping/2024_maree_info/maree_info_format.pkl')
    df = df[df['coef'] > 100]
    print(len(df))
    # Reorganize columns
    df = df[['title', 'tide', 'height', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'coef', 'location_name']]
    # # Target : "title;desc;long_desc;start_date;end_date;location_uid;link;img;keyword;location_name"
    # Rename columns
    df.columns = ['title', 'desc', 'long_desc', 'start_date', 'end_date', 'location_uid', 'link', 'img', 'keyword', 'location_name']

    print(df.head(2))
    df.to_csv('scraping/2024_maree_info/maree_info_format.csv', index=False, sep=';')


# create_df()
# format_df()
format_csv()
