import re
from django.shortcuts import render
from googleapiclient.discovery import build
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import praw  # Импортируем PRAW для работы с Reddit

# Убедитесь, что VADER загружен
nltk.download('vader_lexicon')

# Настройка Reddit API
reddit = praw.Reddit(client_id='B2Gcc5A3cWdUvBZ6oWvetg',
                     client_secret='nf3SO5phIQ5s200LXkmb4v7hdvyhbA',
                     user_agent='social_media_analysis/1.0 by /u/Happy_Cow_9698')

API_KEY = 'AIzaSyAWVF6sSwhFIYJKwhUpKPqEdOlpVx7bfOE'
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_video_details(video_id):
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    return video_response['items'][0]['snippet']

def get_video_comments(video_id):
    comments = []
    response = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    ).execute()

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return comments

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)['compound']
    return score

def analyze_view(request):
    if request.method == 'POST':
        reddit_url = request.POST.get('reddit_url')
        youtube_url = request.POST.get('youtube_url')

        reddit_results = []
        youtube_results = []

        # Анализ Reddit
        if reddit_url:
            # Извлечение идентификатора поста из URL
            url_parts = reddit_url.split('/')
            post_id = url_parts[-3]  # Получаем ID поста

            try:
                submission = reddit.submission(id=post_id)
                sentiment = analyze_sentiment(submission.title)
                reddit_results.append({
                    'title': submission.title,
                    'sentiment': sentiment,
                    'url': reddit_url
                })

                # Анализ комментариев к посту
                submission.comments.replace_more(limit=0)  # Загрузить все комментарии
                for comment in submission.comments.list():
                    comment_sentiment = analyze_sentiment(comment.body)
                    reddit_results.append({
                        'title': comment.body,
                        'sentiment': comment_sentiment,
                        'url': reddit_url
                    })

            except Exception as e:
                print(f"Ошибка при получении данных из Reddit: {e}")

        # Анализ YouTube
        if youtube_url:
            video_id = re.search(r'(?<=v=)[^&]+', youtube_url) or re.search(r'(?<=be/)[^&]+', youtube_url)
            if video_id:
                video_id = video_id.group(0)  # Получаем ID видео

                video_details = get_video_details(video_id)
                video_description = video_details['description']
                description_sentiment = analyze_sentiment(video_description)

                # Получаем и анализируем комментарии
                comments = get_video_comments(video_id)
                comments_sentiment = [analyze_sentiment(comment) for comment in comments]

                youtube_results.append({
                    'title': video_details['title'],
                    'description': video_description,
                    'description_sentiment': description_sentiment,
                    'comments_sentiment': comments_sentiment,
                    'url': youtube_url
                })

        return render(request, 'analysis/result.html', {
            'reddit_results': reddit_results,
            'youtube_results': youtube_results
        })

    return render(request, 'analysis/analyze.html')
