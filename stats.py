from urlextract import URLExtract
import pandas as pd
from collections import Counter
from wordcloud import WordCloud

import emoji


extract = URLExtract()


def fetchstats(selected_user, df):

    # if the selected user is a specific user,then make changes in the dataframe,else do not make any changes

    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]

    num_messages = df.shape[0]
    words = []
    for message in df['Message']:
        words.extend(message.split())

    # counting the number of media files shared
    
    # Check for various media type messages
    # Note: These strings depend on the specific WhatsApp export language/version
    mediaommitted = df[df['Message'].str.contains('image omitted|video omitted|sticker omitted|audio omitted', case=False, na=False)]

    links = []
    for message in df['Message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), mediaommitted.shape[0], len(links)


def get_media_breakdown(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]
        
    media_df = df[df['Message'].str.contains('image omitted|video omitted|sticker omitted|audio omitted', case=False, na=False)]
    
    type_counts = {
        'Image': media_df['Message'].str.count('image omitted').sum(),
        'Video': media_df['Message'].str.count('video omitted').sum(),
        'Sticker': media_df['Message'].str.count('sticker omitted').sum(),
        'Audio': media_df['Message'].str.count('audio omitted').sum()
    }
    
    return pd.DataFrame(list(type_counts.items()), columns=['Media Type', 'Count'])


def get_most_media_users(df):
    media_df = df[df['Message'].str.contains('image omitted|video omitted|sticker omitted|audio omitted', case=False, na=False)]
    user_counts = media_df['User'].value_counts().head(10)
    return user_counts


# most busy users {group level}

def fetchbusyuser(df):

    df = df[df['User'] != 'Group Notification']
    count = df['User'].value_counts().head()

    newdf = pd.DataFrame((df['User'].value_counts()/df.shape[0])*100)
    return count, newdf


def createwordcloud(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['User'] == selected_user]

    wc = WordCloud(width=500, height=500,
                   min_font_size=10, background_color='white')

    text = df['Message'].astype(str).str.cat(sep=" ")
    
    if not text.strip():
        return None

    try:
        df_wc = wc.generate(text)
    except ValueError:
        return None

    return df_wc


# get most common words,this will return a dataframe of
# most common words

def getcommonwords(selecteduser, df):

    # getting the stopwords

    file = open('stop_hinglish.txt', 'r')
    stopwords = file.read()
    stopwords = stopwords.split('\n')

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    temp = df[(df['User'] != 'Group Notification') |
              (df['User'] != '<Media omitted>')]

    words = []

    for message in temp['Message']:
        for word in message.lower().split():
            if word not in stopwords:
                words.append(word)

    mostcommon = pd.DataFrame(Counter(words).most_common(20))
    if mostcommon.empty:
        return pd.DataFrame(columns=['Word', 'Count'])
    
    mostcommon = mostcommon.rename(columns={0: 'Word', 1: 'Count'})
    return mostcommon


def getemojistats(selecteduser, df):

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    emojis = []
    for message in df['Message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emojidf = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    
    if emojidf.empty:
        return pd.DataFrame(columns=['Emoji', 'Count'])

    emojidf = emojidf.rename(columns={0: 'Emoji', 1: 'Count'})

    return emojidf


def monthtimeline(selecteduser, df):

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    temp = df.groupby(['Year', 'Month_num', 'Month']).count()[
        'Message'].reset_index()

    time = []
    for i in range(temp.shape[0]):
        time.append(temp['Month'][i]+"-"+str(temp['Year'][i]))

    temp['Time'] = time

    return temp


def monthactivitymap(selecteduser, df):

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    return df['Month'].value_counts()


def weekactivitymap(selecteduser, df):

    if selecteduser != 'Overall':
        df = df[df['User'] == selecteduser]

    return df['Day_name'].value_counts()
