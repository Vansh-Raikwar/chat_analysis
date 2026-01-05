import re
import pandas as pd

def preprocess(data):
    pattern = r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}:\d{1,2}\s[\w\s]+\]\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_messages': messages, 'message_date': dates})

    # Remove brackets and trailing characters from date strings
    df['message_date'] = df['message_date'].apply(lambda x: x.strip('[] ').replace('\u202f', ' '))
    
    # Parse dates with AM/PM
    df['date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M:%S %p')

    users = []
    messages = []

    for message in df['user_messages']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('Group Notification')
            messages.append(entry[0])

    df['User'] = users
    df['message'] = messages
    
    # Strip whitespace
    df['message'] = df['message'].apply(lambda text: text.strip())

    df = df.drop(['user_messages', 'message_date'], axis=1)
    
    # Rename columns to match stats.py expectations
    df = df.rename(columns={'message': 'Message', 'date': 'Date'})

    df['Only date'] = df['Date'].dt.date
    df['Year'] = df['Date'].dt.year
    df['Month_num'] = df['Date'].dt.month
    df['Month'] = df['Date'].dt.month_name()
    df['Day'] = df['Date'].dt.day
    df['Day_name'] = df['Date'].dt.day_name()
    df['Hour'] = df['Date'].dt.hour
    df['Minute'] = df['Date'].dt.minute

    return df
