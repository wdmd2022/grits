# Design of the Project

The API/SPA we are building is going to allow for the quick and easy retrieval of the 150 Metrical Psalms put forth by the Scottish Presbyterian church in the year 1650.

The fit to the theme of “Lost in Space” comes by way of the music we will use and present alongside the retrieved records — each psalm will be parsed to identify # of stanzas and have assigned to it a certain song link that matches this. In the frontend, we’ll be able to play these specific songs alongside the individual stanzas, in syncopation, using JS. This design could easily be adapted to serve other ancient texts that fit various meters. But, the song we are using today was picked very specifically to fit the theme: it is an adaptation of ‘Ghost Riders in the Sky’ (sounds like aliens to me!) that is edited to reflect the stanza # of each psalm record.

To get the base psalm records, we will first scrape a website from 20 years ago that has them stored on different HTML pages. To do this, we’ll use python and the requests library as it is just 150 records.

Because the records are in a variety of formatting conventions — some with the stanzas in their own elements, some not, some with multiple versions — we’ll parse it using Beautiful Soup and get the information into Pandas DataFrames to make it really easy to upload into our MySQL server.

From a technical perspective, we will be using a docker-compose file that will spin up several servers and processes:

- a python-based data pre-processor that will have access to our scraped raw HTML files
-  a MySQL server to store our psalm and stanza and user records
- a Flask server to serve up our API
- an NginX server to serve up our SPA frontend
- a Redis server to help with caching of our API

Data will be persisted on two volumes, one for the MySQL server and one for the Redis server.

The data pre-processor will first attempt to establish a connection to the MySQL server and once that is done, will parse the HTML records and put them into the database along with our test user record. It will use mysql.connector to establish the initial connection and table creation, and then an SQLAlchemy engine to connect pandas to the database for the actual upload. The records will have certain fields including timestamps for the stanzas in a given psalm, allowing for easy playback later along with our JS player components.

The API server will function as outlined in the API documentation. Under the hood, it will use Redis for caching the results of queries. Authentication will be done using API keys and an authentication function will wrap the response functions of the server. SQLAlchemy will handle our database transactions.

On the frontend, users will be able to log in with their username and API key (user creation will be in a future iteration) and will be presented with a filterable list of psalms to choose from. On the psalm detail page, we’ll use the rabbit-lyrics JS library for its dependency-free simple audio player. We’ll use the timestamps from the individual stanza records to set our music up to follow the words. Song variations will be made by editing a MIDI file in GarageBand. The SPA will be written in vanilla JS; the narrow scope of the application makes this a sensible choice. Future iterations with a more complicated database and selection of songs/meters would probably require a framework. API Key will be held in LocalStorage to submit within the header of requests.

I will expect to spend the vast majority of time on the back-end, especially the data parsing side. Beautiful Soup in particular is new to me. 
