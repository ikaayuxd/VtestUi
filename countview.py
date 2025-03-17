import time
import requests

BOT_TOKEN = '7333437316:-'
CHANNEL_ID = '@'  
VIEW_THRESHOLD = 500000  
WAIT_TIME = 1800  
API_URL = 'https://api.telegram.org'

def get_posts():
    url = f"{API_URL}/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url).json()
    posts = [update['message'] for update in response['result'] if 'message' in update and 'text' in update['message']]
    return posts

def get_post_views(post_id):
    url = f"{API_URL}/bot{BOT_TOKEN}/getMessage?chat_id={CHANNEL_ID}&message_id={post_id}"
    response = requests.get(url).json()
    return response['result'].get('views', 0)

def process_posts():
    posts = get_posts()
    for post in posts:
        post_id = post['message_id']
        while True:
            views = get_post_views(post_id)
            if views >= VIEW_THRESHOLD:
                print(f"Post {post_id} has reached {VIEW_THRESHOLD} views.")
                break
            print(f"Waiting for post {post_id} to reach {VIEW_THRESHOLD} views. Current views: {views}")
            time.sleep(WAIT_TIME)

        time.sleep(WAIT_TIME) 

def handler(request):
    process_posts()
    return {
        "statusCode": 200,
        "body": "Posts processed successfully."
    }
