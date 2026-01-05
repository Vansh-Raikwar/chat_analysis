import streamlit as st
import preprocess
import re
import stats
import matplotlib.pyplot as plt
import numpy as np


st.sidebar.title("Whatsapp Chat Analyzer")

# this is for uploading a file
uploaded_file = st.sidebar.file_uploader("← Choose a file")

if uploaded_file is None:
    st.title("Whatsapp Chat Analysis")
    st.title("← upload a file from sidebar")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    # converting the bytecode to the text-file

    data = bytes_data.decode("utf-8")

    # sending the file data to the preprocess function for further functioning

    df = preprocess.preprocess(data)

    # displaying the dataframe

    # st.dataframe(df)

    # fetch unique users
    user_list = df['User'].unique().tolist()

    # removing the groupnotification

    if 'Group Notification' in user_list:
        user_list.remove('Group Notification')

    # organinsing things
    user_list.sort()

    # including overall,this will be responsible for showcasing the  overall chat group analysis

    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox(
        "Show analysis with respect to", user_list)

    st.title("Whats App Chat Analysis for " + selected_user)
    if st.sidebar.button("Show Analysis"):

        # getting the stats of the selected user from the stats script

        num_messages, num_words, media_omitted, links = stats.fetchstats(
            selected_user, df)

        # first phase is to showcase the basic stats like number of users,number of messages,number of media shared and all,so for that i requrire the 4 columns

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.title("Total Messages")
            st.title(num_messages)
        with col2:
            st.title("Total No.of Words")
            st.title(num_words)
        with col3:
            st.title("No. of Media Shared")
            st.title(media_omitted)
        with col4:
            st.title("Total Links Shared")
            st.title(links)

        # finding the busiest users in the group

        if selected_user == 'Overall':

            # dividing the space into two columns
            # first col is the bar chart and the second col is the dataframe representing the

            st.title('Most Busy Users')
            busycount, newdf = stats.fetchbusyuser(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(busycount.index, busycount.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(newdf)

        # Word Cloud

        st.title('Word Cloud')
        df_img = stats.createwordcloud(selected_user, df)
        
        if df_img is not None:
            fig, ax = plt.subplots()
            ax.imshow(df_img)
            st.pyplot(fig)
        else:
            st.info("Not enough words to generate user word cloud.")

        # most common words in the chat

        most_common_df = stats.getcommonwords(selected_user, df)
        
        if not most_common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(most_common_df['Word'], most_common_df['Count'])
            plt.xticks(rotation='vertical')
            st.title('Most commmon words')
            
            st.pyplot(fig)
            
        else:
            st.info("Not enough data to find common words.")

        # Emoji Analysis

        emoji_df = stats.getemojistats(selected_user, df)
        # emoji_df.columns assignment removed as stats.py now handles it

        st.title("Emoji Analysis")
        
        if not emoji_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                emojicount = list(emoji_df['Count'])
                perlist = [(i/sum(emojicount))*100 for i in emojicount]
                emoji_df['Percentage use'] = np.array(perlist)
                st.dataframe(emoji_df)
        else:
            st.info("No emojis found in the selected chat.")

        # Monthly timeline

        st.title("Monthly Timeline")
        time = stats.monthtimeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(time['Time'], time['Message'], color='green')
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        st.pyplot(fig)

        # Media Analysis
        st.title("Media Analysis")
        media_df = stats.get_media_breakdown(selected_user, df)
        
        if not media_df.empty and media_df['Count'].sum() > 0:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(media_df)
                if selected_user == 'Overall':
                    st.write("Top 3 Media Senders")
                    media_user_counts = stats.get_most_media_users(df)
                    st.dataframe(media_user_counts.head(3))

            with col2:
                fig, ax = plt.subplots()
                if selected_user == 'Overall':
                    ax.bar(media_user_counts.index, media_user_counts.values)
                    plt.xticks(rotation='vertical')
                else:
                    ax.bar(media_df['Media Type'], media_df['Count'])
                    plt.xticks(rotation='vertical')
                st.pyplot(fig)
        else:
             st.info("No media shared in this chat.")

             st.info("No media shared in this chat.")

        if selected_user == 'Overall':
            st.title("Who Sent Maximum Media")
            media_user_counts = stats.get_most_media_users(df)
            if not media_user_counts.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig, ax = plt.subplots()
                    ax.bar(media_user_counts.index, media_user_counts.values, color='cyan')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                     st.dataframe(media_user_counts)
            else:
                st.info("No media usage data available.")

        # Activity maps

        st.title("Activity Maps")

        col1, col2 = st.columns(2)

        with col1:

            st.header("Most Busy Day")

            busy_day = stats.weekactivitymap(selected_user, df)

            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)

        with col2:

            st.header("Most Busy Month")
            busy_month = stats.monthactivitymap(selected_user, df)

            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            plt.tight_layout()
            st.pyplot(fig)
