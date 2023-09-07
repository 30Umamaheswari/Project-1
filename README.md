# YouTube Data Harvesting and Warehousing using SQL, MongoDB, and Streamlit

## Skills Gained from This Project

- Python scripting
- Data collection from YouTube API
- MongoDB data management (using Atlas)
- SQL database management
- Building a Streamlit web application
- API integration
- Data analysis and visualization

## Domain

Social Media

## Problem Statement

The goal of this project is to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels. The application should offer the following features:

1. Ability to input a YouTube channel ID and retrieve relevant data (channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each video) using the Google API.

2. Option to store the collected data in a MongoDB database as a data lake.

3. Ability to collect data for up to 10 different YouTube channels and store them in the data lake with a single click.

4. Option to select a channel name and migrate its data from the data lake to a SQL database as tables.

5. Ability to search and retrieve data from the SQL database using various search options, including joining tables to get channel details.

## Approach

1. **Set up a Streamlit App**: Utilize Streamlit to build a user-friendly web application where users can input a YouTube channel ID, view channel details, and select channels for migration to the data warehouse.

2. **Connect to the YouTube API**: Employ the Google API client library for Python to make requests to the YouTube API, fetching channel and video data.

3. **Store Data in a MongoDB Data Lake**: After retrieving data from the YouTube API, store it in a MongoDB data lake. MongoDB is chosen for its capability to handle unstructured and semi-structured data effectively.

4. **Migrate Data to a SQL Data Warehouse**: Once data has been collected for multiple channels, migrate it to a SQL data warehouse, using a SQL database like MySQL or PostgreSQL.

5. **Query the SQL Data Warehouse**: Utilize SQL queries, possibly with a Python SQL library like SQLAlchemy, to join tables within the SQL data warehouse and retrieve data for specific channels based on user input.

6. **Display Data in the Streamlit App**: Finally, present the retrieved data in the Streamlit app. Take advantage of Streamlit's data visualization features to create charts and graphs, aiding users in analyzing the data.

## SQL Query Outputs Displayed in the Streamlit Application

1. What are the names of all the videos and their corresponding channels?
2. Which channels have the most number of videos, and how many videos do they have?
3. What are the top 10 most viewed videos and their respective channels?
4. How many comments were made on each video, and what are their corresponding video names?
5. Which videos have the highest number of likes, and what are their corresponding channel names?
6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?
7. What is the total number of views for each channel, and what are their corresponding channel names?
8. What are the names of all the channels that have published videos in the year 2022?
9. What is the average duration of all videos in each channel, and what are their corresponding channel names?
10. Which videos have the highest number of comments, and what are their corresponding channel names?

## Results

This project aims to develop a user-friendly Streamlit application that utilizes the Google API to extract information from YouTube channels, stores it in a MongoDB database, migrates it to a SQL data warehouse, and enables users to search for channel details and join tables to view data in the Streamlit app. This tool will assist users in accessing valuable insights from YouTube data in a structured and efficient manner.
