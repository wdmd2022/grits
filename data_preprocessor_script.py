import re
from bs4 import BeautifulSoup
import pandas as pd
import os
import mysql.connector
import time



# define a function to check that our database has been created
def first_connect_to_the_database():
    while True:
        try:
            return mysql.connector.connect(host=os.environ['MYSQL_HOST'],
                                           user=os.environ['MYSQL_USER'],
                                           password=os.environ['MYSQL_PASSWORD'],
                                           database=os.environ['MYSQL_DATABASE'])
        except mysql.connector.Error as whoops:
            print(f"Whoops! it didn't work: {whoops}")
            time.sleep(5)

# let's use it to make sure that database is actually available
my_connection = first_connect_to_the_database()
print("awesome we did it")

psalms_data = []
stanzas_data = []

for psalm_num in range(1, 151):
    file_path = f'/data_sources/psalm-{str(psalm_num).zfill(2)}.html'

    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    pre_tags = soup.find_all('pre')
    stanzas = []
    stanza_count = 0

    for pre_tag in pre_tags:
        if re.match(r'\s*1', pre_tag.get_text(strip=True)):
            stanzas.append(pre_tag.get_text(strip=True))
            stanza_count += 1
            stanzas_data.append({
                'PsalmNumber': psalm_num,
                'StanzaNumber': stanza_count,
                'Meter': 'common',
                'StanzaText': pre_tag.get_text(strip=True)
            })
            for sibling in pre_tag.find_next_siblings('pre'):
                stanza_text = sibling.get_text(strip=True)
                stanzas.append(stanza_text)
                stanza_count += 1
                stanzas_data.append({
                    'PsalmNumber': psalm_num,
                    'StanzaNumber': stanza_count,
                    'Meter': 'common',
                    'StanzaText': stanza_text
                })
            break
    psalms_data.append({
        'Number': psalm_num,
        'Title': f'Psalm {psalm_num}',
        'Meter': 'common',
        'PsalmText': '\n\n'.join(stanzas),
        'Stanzas': stanza_count
    })

# let's put our lists into dataframes
psalms_df = pd.DataFrame(psalms_data)
stanzas_df = pd.DataFrame(stanzas_data)

print(psalms_df)

# psalms_df.to_csv('psalms5.csv', index=False, encoding='utf-8')
# stanzas_df.to_csv('stanzas5.csv', index=False, encoding='utf-8')

print("nice, it got to the end. You are a great coder. See you later.")
