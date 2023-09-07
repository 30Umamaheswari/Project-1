import mysql
import pandas as pd
import streamlit as st
from pymongo import MongoClient
import mysql.connector
from googleapiclient.discovery import build
from streamlit_option_menu import option_menu

api_key = 'AIzaSyDSdirW9QW42I2R5cJH3ZEn9IsA0SpBZMw'
youtube_api = build('youtube', 'v3', developerKey=api_key)

video_ids = []
comment_id = ''

import re


def calculate_average_duration(rows):
    channel_durations = {}
    channel_video_count = {}

    for row in rows:
        channel_title, video_duration = row
        if channel_title not in channel_durations:
            channel_durations[channel_title] = 0
            channel_video_count[channel_title] = 0

        # Extract hours, minutes, and seconds from ISO 8601 duration format
        duration_parts = re.findall(r'(\d+)([HMS])', video_duration)
        total_seconds = 0

        for value, unit in duration_parts:
            if unit == 'H':
                total_seconds += int(value) * 3600
            elif unit == 'M':
                total_seconds += int(value) * 60
            elif unit == 'S':
                total_seconds += int(value)

        channel_durations[channel_title] += total_seconds
        channel_video_count[channel_title] += 1

    avg_duration_data = []
    for channel_title in channel_durations:
        average_duration_seconds = channel_durations[channel_title] / channel_video_count[channel_title]
        avg_duration_data.append([channel_title,
                                  f"{int(average_duration_seconds // 3600):02}:{int((average_duration_seconds % 3600) // 60):02}:{int(average_duration_seconds % 60):02}"])

    return avg_duration_data


def playlist_datas(c_id):
    pl_data = []
    token = None

    while True:
        request = youtube_api.playlists().list(
            part="snippet,player,status,contentDetails",
            maxResults=50,
            channelId=c_id,
            pageToken=token
        )
        response = request.execute()

        for i in response['items']:
            playlist_data = {
                "channel_id": i["snippet"]['channelId'],
                "channel_name": i["snippet"]['channelTitle'],
                'playlist_id': i['id'],
                "playlist_name": i["snippet"]["title"],
                "playlist_video_count": int(i["contentDetails"]["itemCount"]),
                "playlist_status": i["status"]["privacyStatus"],
                "playlist_published_at": i["snippet"]["publishedAt"]
            }
            pl_data.append(playlist_data)

        token = response.get('nextPageToken')

        if response.get('nextPageToken') is None:
            break
    return pl_data


def video_id_data(p):
    global video_ids
    token = None

    while True:
        request = youtube_api.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=50,
            playlistId=p,
            pageToken=token
        )
        response = request.execute()

        for i in response['items']:
            video_ids.append(i['contentDetails']['videoId'])
            token = response.get('nextPageToken')

        if response.get('nextPageToken') is None:
            break

    return video_ids


def get_comment_datas(comment_ids):
    comment_info = []
    for i in range(len(comment_ids)):
        try:
            comment_response = youtube_api.commentThreads().list(
                part="snippet,id,replies",
                videoId=comment_ids[i],
                maxResults=100
            ).execute()

            for comment in comment_response['items']:
                global comment_id
                # if comment_text.startswith("<") and comment_text.endswith(">"):
                #     comment_text = BeautifulSoup(comment_text, "html.parser").get_text()

                comment_data = {
                    "video_id": comment_ids[i],
                    "comment_id": comment['snippet']['topLevelComment']['id'],
                    "comment_text": comment['snippet']['topLevelComment']['snippet']['textOriginal'],
                    "comment_author": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    "comment_published_at": comment['snippet']['topLevelComment']['snippet']['publishedAt']
                }
                comment_info.append(comment_data)
        except Exception as e:
            comment_info.append({
                "video_id": comment_ids[i],
                "comment_id": comment['snippet']['topLevelComment']['id'],
                "comment_text": "Comment is not accessible",
                "comment_author": "NA",
                "comment_published_at": "NA"
            })
            # print('error: ', e)

    return comment_info


def get_video_data(v):
    list_video_data = []
    for i in range(len(v)):
        video_id = v[i]

        video_response = youtube_api.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()

        video_data = {
            "channel_id": video_response["items"][0]["snippet"]['channelId'],
            "channel_title": video_response["items"][0]["snippet"]['channelTitle'],
            "video_id": video_id,
            "video_name": video_response["items"][0]["snippet"]["title"],
            "video_description": video_response["items"][0]["snippet"]["description"],
            "video_view_count": int(video_response["items"][0]["statistics"].get("viewCount", 0)),
            "video_favorite": int(video_response["items"][0]["statistics"].get("favoriteCount", 0)),
            "video_likes": int(video_response["items"][0]["statistics"].get("likeCount", 0)),
            "video_dislikes": int(video_response["items"][0]["statistics"].get("dislikeCount", 0)),
            "video_comments_count": int(video_response["items"][0]["statistics"].get("commentCount", 0)),
            "video_duration": video_response["items"][0]["contentDetails"]["duration"],
            "video_thumbnail": video_response["items"][0]["snippet"]["thumbnails"],
            "video_caption_status": "Available" if "caption" in video_response["items"][0][
                "contentDetails"] else "Unavailable",
            "video_published_at": video_response["items"][0]["snippet"]["publishedAt"],
        }

        # if video_data["video_comments_count"] > 0:
        #     video_data["video_comments"] = get_comment_datas(video_id)
        # # else:
        #     video_data["video_comments"] = ['No comments']

        list_video_data.append(video_data)

    return list_video_data


def get_channel_status(c_id):
    response = youtube_api.channels().list(
        part="snippet,statistics,contentDetails",
        id=c_id
    ).execute()

    if "items" in response:
        playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # global v_ids
        video_id_data(playlist_id)

        channel_data = {
            "channel_id": str(response["items"][0]["id"]),
            "channel_title": response["items"][0]["snippet"]["title"],
            "channel_description": response["items"][0]["snippet"]["description"],
            "channel_hidden_subscriber_count": int(response["items"][0]["statistics"]["hiddenSubscriberCount"]),
            "channel_subscriber_count": int(response["items"][0]["statistics"]["subscriberCount"]),
            "channel_video_count": int(response["items"][0]["statistics"]["videoCount"]),
            "channel_view_count": int(response["items"][0]["statistics"]["viewCount"])
        }
        return channel_data


def channel_details(ch_id):
    c = get_channel_status(ch_id)
    p = playlist_datas(ch_id)
    v = get_video_data(video_ids)
    com = get_comment_datas(video_ids)

    datas = {'channel_info': c,
             'playlist_info': p,
             'video_info': v,
             'comment_info': com}
    return datas


def main():
    st.set_page_config(page_title="Youtube Data",
                       layout="wide",
                       initial_sidebar_state="auto", )

    drive_link = "https://drive.google.com/file/d/1u_kJruJe7u9VEEpYIvuWNmEJG9zB78LR/view?usp=drive_link"
    file_id = drive_link.split("/file/d/")[1].split("/view")[0]
    direct_download_link = f"https://drive.google.com/uc?id={file_id}"
    page_bg_img = f"""
    <style>
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.5);  /* Make sidebar background slightly transparent */
        backdrop-filter: blur(10px);  /* Apply blur effect to the sidebar background */
    }}

    [data-testid="stAppViewContainer"] {{
        background-image: url("{direct_download_link}");
        background-size: cover;
    }}
    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.title(':blue[Youtube Data Retrieving and Storing in different DB]')
    with st.sidebar:
        selected = option_menu('Harvesting Menu', ["Retrieve & Store", "Data Analysis"],
                               default_index=0,
                               orientation="vertical",
                               styles={"nav-link": {"font-size": "15px", "text-align": "centre", "margin": "0px",
                                                    "--hover-color": "#98CDDE"},
                                       "container": {"max-width": "6000px"},
                                       "nav-link-selected": {"background-color": "#17A0DA"}})

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Umamaheswari30*",
        database="youtube"
    )
    cursor = mydb.cursor()

    if selected == "Retrieve & Store":
        tab1, tab2 = st.tabs(["$\huge RETRIEVE $", "$\huge STORE $"])
        with tab1:
            custom_css = """
            <style>
            label {
                color: #09485E; /* Set the desired color */
            }
            </style>
            """
            st.markdown(custom_css, unsafe_allow_html=True)

            ch_id = st.text_input('Enter your Channel id')
            if ch_id and st.button("Get Data"):
                data = channel_details(ch_id)
                df = pd.DataFrame(data['channel_info'], index=['Keys'])
                w = st.expander('Channel details')
                w.dataframe(df)

                pld = data['playlist_info']
                y = st.expander('Playlist details')
                y.dataframe(pld)

                vd = data['video_info']
                z = st.expander('Video details')
                z.dataframe(vd)

                cmd = data['comment_info']
                x = st.expander('Comment details')
                x.dataframe(cmd)

                st.markdown(f'<div style="color: royalblue; font-weight: bold; font-size: 20px;">Your Data was successfully Retrived</div>',
                            unsafe_allow_html=True)

            if st.button('Store Data'):
                client = MongoClient('mongodb://localhost:27017/')
                db = client['youtube']
                collections = db['channel_details']

                d = channel_details(ch_id)

                collections.insert_one(d)
                client.close()
                st.markdown(
                    f'<div style="color: royalblue; font-weight: bold; font-size: 20px;">Your datas are successfully stored</div>',
                    unsafe_allow_html=True)

        with tab2:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['youtube']
            collections = db['channel_details']

            channel_names = [i['channel_info']['channel_title'] for i in collections.find()]
            selected_channel = st.selectbox('Select one channel', options=channel_names)

            if st.button('Migrate Data'):
                for x in collections.find({'channel_info.channel_title': selected_channel}):
                    # Extract channel data
                    channel_data = x['channel_info']

                    # Insert channel data into MySQL table 'channel_data'
                    channel_values = (
                        channel_data['channel_id'],
                        channel_data['channel_title'],
                        channel_data['channel_description'],
                        channel_data['channel_hidden_subscriber_count'],
                        channel_data['channel_subscriber_count'],
                        channel_data['channel_video_count'],
                        channel_data['channel_view_count']
                    )

                    query = "INSERT INTO channel_data (channel_id, channel_title, channel_description, channel_hidden_subscriber_count, " \
                            "channel_subscriber_count, channel_video_count, channel_view_count) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, channel_values)
                    mydb.commit()

                    # Extract playlist data
                    playlist_data = x['playlist_info']

                    # Insert playlist data into MySQL table 'playlist_data'
                    for playlist in playlist_data:
                        playlist_values = (
                            playlist['channel_id'],
                            playlist['channel_name'],
                            playlist['playlist_id'],
                            playlist['playlist_name'],
                            playlist['playlist_video_count'],
                            playlist['playlist_status'],
                            playlist['playlist_published_at']
                        )

                        query = "INSERT INTO playlist_data (channel_id, channel_name, playlist_id, playlist_name, playlist_video_count, " \
                                "playlist_status, playlist_published_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(query, playlist_values)
                        mydb.commit()

                    # Extract video data
                    video_data = x['video_info']

                    # Insert video data into MySQL table 'video_data'
                    for video in video_data:
                        video_values = (
                            video['channel_id'],
                            video['channel_title'],
                            video['video_id'],
                            video['video_name'],
                            video['video_description'],
                            video['video_view_count'],
                            video['video_favorite'],
                            video['video_likes'],
                            video['video_dislikes'],
                            video['video_comments_count'],
                            video['video_duration'],
                            video['video_caption_status'],
                            video['video_published_at']
                        )

                        query = "INSERT INTO video_data (channel_id, channel_title, video_id, video_name, video_description, video_view_count, " \
                                "video_favorite, video_likes, video_dislikes, video_comments_count, video_duration, " \
                                "video_caption_status, video_published_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(query, video_values)
                        mydb.commit()

                    # Extract comment data
                    comment_data = x['comment_info']

                    # Insert comment data into MySQL table 'comment_data'
                    for comment in comment_data:
                        comment_values = (
                            comment['video_id'],
                            comment['comment_id'],
                            comment['comment_text'],
                            comment['comment_author'],
                            comment['comment_published_at']
                        )

                        check_query = "SELECT COUNT(*) FROM comment_data WHERE comment_id = %s"
                        cursor.execute(check_query, (comment['comment_id'],))
                        count = cursor.fetchone()[0]

                        if count == 0:
                            # Comment not present, so insert it
                            query = "INSERT INTO comment_data (video_id, comment_id, comment_text, comment_author, comment_published_at) " \
                                    "VALUES (%s, %s, %s, %s, %s)"
                            cursor.execute(query, comment_values)
                            mydb.commit()

                        # query = "INSERT INTO comment_data (video_id, comment_id, comment_text, comment_author, comment_published_at) " \
                        #         "VALUES (%s, %s, %s, %s, %s)"
                        # cursor.execute(query, comment_values)
                        # mydb.commit()

                    # Close the MongoDB connection after all inserts are done
                    client.close()
                    st.markdown(
                        f'<div style="color: royalblue; font-weight: bold; font-size: 20px;">Data from MongoDB collections successfully stored in MySQL tables</div>',
                        unsafe_allow_html=True)

    if selected == "Data Analysis":
        # st.write('Choose any one filter')
        filter_data = st.selectbox('Choose any one filter',
                                   ['To view the names of all the videos and their corresponding channels.',
                                    'To view which channels have the most number of videos, and view how many videos that they have.',
                                    'The top 10 most viewed videos and their respective channels.',
                                    'Total comments were made on each video, and their corresponding video names.',
                                    'To view which videos have the highest number of likes, and their corresponding channel names.',
                                    'The total number of likes and dislikes for each video, and their corresponding video names.',
                                    'The total number of views for each channel, and their corresponding channel names.',
                                    'The names of all the channels that have published videos in the year 2022.',
                                    'The average duration of all videos in each channel, and their corresponding channel names.',
                                    'To view which videos have the highest number of comments, and their corresponding channel names.'])

        if filter_data == 'To view the names of all the videos and their corresponding channels.':
            cursor.execute(
                "SELECT video_data.video_name, channel_data.channel_title FROM video_data JOIN channel_data ON "
                "video_data.channel_id = channel_data.channel_id")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == ('To view which channels have the most number of videos, and view how many videos that '
                             'they have.'):
            cursor.execute(
                "SELECT channel_data.channel_title, COUNT(video_data.video_id) AS VideoCount FROM channel_data JOIN "
                "video_data ON channel_data.channel_id = video_data.channel_id GROUP BY channel_data.channel_title "
                "ORDER BY VideoCount DESC;")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == 'The top 10 most viewed videos and their respective channels.':
            cursor.execute(
                'SELECT video_data.video_name, channel_data.channel_title, video_data.video_view_count FROM '
                'video_data JOIN channel_data ON video_data.channel_id = channel_data.channel_id ORDER BY '
                'video_data.video_view_count DESC LIMIT 10')
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == 'Total comments were made on each video, and their corresponding video names.':
            cursor.execute(
                "SELECT video_data.video_name, COUNT(comment_data.comment_id) AS CommentCount FROM video_data LEFT "
                "JOIN comment_data ON video_data.video_id = comment_data.video_id GROUP BY video_data.video_name")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == 'To view which videos have the highest number of likes, and their corresponding channel names.':
            cursor.execute(
                "SELECT video_data.video_name, channel_data.channel_title FROM video_data JOIN channel_data ON "
                "video_data.channel_id = channel_data.channel_id ORDER BY video_data.video_likes DESC LIMIT 10")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == 'The total number of likes and dislikes for each video, and their corresponding video names.':
            cursor.execute(
                "SELECT video_data.video_name, SUM(video_data.video_likes) AS TotalLikes, "
                "SUM(video_data.video_dislikes) AS TotalDislikes FROM video_data JOIN channel_data ON "
                "video_data.channel_id = channel_data.channel_id GROUP BY video_data.video_name")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == 'The total number of views for each channel, and their corresponding channel names.':
            cursor.execute(
                "SELECT channel_data.channel_title, SUM(video_data.video_view_count) AS TotalViews FROM channel_data "
                "JOIN video_data ON channel_data.channel_id = video_data.channel_id GROUP BY "
                "channel_data.channel_title")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == 'The names of all the channels that have published videos in the year 2022.':
            cursor.execute(
                "SELECT DISTINCT channel_data.channel_title FROM channel_data JOIN video_data ON "
                "channel_data.channel_id = video_data.channel_id WHERE video_data.video_published_at LIKE '2022%'")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            st.dataframe(df)

        elif filter_data == 'The average duration of all videos in each channel, and their corresponding channel names.':
            cursor.execute("SELECT channel_data.channel_title, video_data.video_duration FROM channel_data JOIN "
                           "video_data ON channel_data.channel_id = video_data.channel_id")
            rows = cursor.fetchall()
            avg_duration_data = calculate_average_duration(rows)
            avg_df = pd.DataFrame(avg_duration_data, columns=["Channel Title", "Average Duration"])

            st.dataframe(avg_df)

        elif filter_data == ('To view which videos have the highest number of comments, and their corresponding '
                             'channel names.'):
            cursor.execute("SELECT video_data.video_name, channel_data.channel_title FROM video_data JOIN "
                           "channel_data ON video_data.channel_id = channel_data.channel_id ORDER BY "
                           "video_data.video_comments_count DESC LIMIT 10")
            df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)

            css = [
                {'selector': 'tr:nth-of-type(odd)', 'props': 'background-color: #398DC7; color: #09485e;'},
                {'selector': 'tr:nth-of-type(even)', 'props': 'background-color: #0668d2; color: #FFFFFF;'}
            ]
            styled_df = df.style.set_table_styles(css)

            st.dataframe(styled_df, width=1200, height=400)


# [theme]
# primaryColor="#0668d2"
# backgroundColor="#1a78c5"
# secondaryBackgroundColor="#17a0da"
# textColor="#09485e"
# font="serif"


if __name__ == '__main__':
    main()
