import re
from bs4 import BeautifulSoup
import pandas as pd
import os
import mysql.connector
import time
from sqlalchemy import create_engine



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

# let's make a function to help us normalize our text data
def normalize_text(text):
    # turn multiple spaces into a single space
    text = re.sub(' +', ' ', text)
    # strip leading and trailing spaces on return
    return text.strip()

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
            stanza_text = normalize_text(pre_tag.get_text())
            stanzas.append(stanza_text)
            stanza_count += 1
            stanzas_data.append({
                'PsalmNumber': psalm_num,
                'StanzaNumber': stanza_count,
                'Meter': 'common',
                'StanzaText': stanza_text
            })
            for sibling in pre_tag.find_next_siblings('pre'):
                stanza_text = normalize_text(sibling.get_text())
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
        'Stanzas': stanza_count,
        'Audio': f'./midi/grits-{stanza_count}.midi'
    })

# let's put our lists into dataframes
psalms_df = pd.DataFrame(psalms_data)
stanzas_df = pd.DataFrame(stanzas_data)

# leaving some old tests up here for posterity's sake
# print(psalms_df)
# psalms_df.to_csv('psalms5.csv', index=False, encoding='utf-8')
# stanzas_df.to_csv('stanzas5.csv', index=False, encoding='utf-8')
# max_length_psalmtext = psalms_df['PsalmText'].apply(len).max()
# print ("max psalm length:", max_length_psalmtext)
# max_length_stanza = stanzas_df['StanzaText'].apply(len).max()
# print("max stanza length:", max_length_stanza)
# unique_staza_counts = psalms_df['Stanzas'].unique()
# unique_stanza_counts_list = list(unique_staza_counts)
# print(unique_stanza_counts_list)
# print(psalms_df.head())
# print("nice, it got to the end. You are a great coder. See you later.")

###################Let's get ready to IMPOOOOOORRRRTTTTTT#####################

# first let's make an SQL query to create our tables. First, psalms:
gimme_a_psalms_table_plz = """
CREATE TABLE IF NOT EXISTS psalms (
    Number INT PRIMARY KEY,
    Title VARCHAR(255),
    Subtitle VARCHAR(255),
    Meter VARCHAR(50),
    PsalmText TEXT,
    Stanzas INT,
    Audio VARCHAR(255)
);
"""
# and one to create our stanzas table, which will link to psalms
gimme_a_stanzas_table_plz = """
CREATE TABLE IF NOT EXISTS stanzas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    PsalmNumber INT,
    StanzaNumber INT,
    Meter VARCHAR(50),
    StanzaText TEXT,
    FOREIGN KEY (PsalmNumber) REFERENCES psalms(Number)
);
"""

# and also one to create our users table, where we will store our api keys
gimme_a_users_table_plz = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL
);
"""

make_a_test_user_plz = """
INSERT INTO users (username, api_key)
VALUES ('llcooldoug', 't3stk3y1337');
"""

# and we can use the connection we established earlier to create a cursor and
# execute our commands. Once that's done, we'll just commit the changes and
# close that connection before turning to sqlalchemy to enable a super easy upload
# without the ardor of looping through our dataframe manually to push each record.

cursor = my_connection.cursor()
cursor.execute(gimme_a_psalms_table_plz)
cursor.execute(gimme_a_stanzas_table_plz)
cursor.execute(gimme_a_users_table_plz)
cursor.execute(make_a_test_user_plz)
my_connection.commit()
my_connection.close()

print("tables have been created!")

# here we are going to create a sqlalchemy engine, because that's the way that
# pandas requires us to feed it an engine (really any sqlalchemy-compat one)
alc_dialect_driver = 'mysql+mysqlconnector'
alc_user = os.environ['MYSQL_USER']
alc_pass = os.environ['MYSQL_PASSWORD']
alc_host = os.environ['MYSQL_HOST']
alc_db = os.environ['MYSQL_DATABASE']
alchemy_engine = create_engine(
    f"{alc_dialect_driver}://{alc_user}:{alc_pass}@{alc_host}/{alc_db}"
)

# now we can use the aptly-named 'to_sql' function in pandas to get it in!
psalms_df.to_sql(
    'psalms',
    con=alchemy_engine,
    if_exists='append',
    index=False
)
stanzas_df.to_sql(
    'stanzas',
    con=alchemy_engine,
    if_exists='append',
    index=False
)

print("data is in, you are a winner")
