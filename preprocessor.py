import re
import pandas as pd


def preprocess(data):
    pattern = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APM]{2}\s-\s"
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    # Create DataFrame
    df = pd.DataFrame({'user_message': messages, 'date': dates})

    # Clean up the date column
    df['date'] = (
        df['date']
        .str.replace('\u202f', ' ', regex=True)  # Fix non-breaking space
        .str.replace(r' - $', '', regex=True)    # Remove trailing "- "
        .str.strip()                             # Remove whitespace
    )

    # Convert to datetime
    df['date'] = pd.to_datetime(df['date'], format="%m/%d/%y, %I:%M %p", errors='coerce')

    # Extract user and message
    df[['user', 'message']] = df['user_message'].str.extract(r'^(.*?):\s(.+)', expand=True)

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:  # user name
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])


    # Drop original user_message column
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional time-based columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['minute'] = df['date'].dt.minute
    df['hour'] = df['date'].dt.hour
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['month'] = df['date'].dt.month_name()

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df

