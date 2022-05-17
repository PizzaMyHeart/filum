import requests
from datetime import datetime
import pprint

class Download:
    def __init__(self, url):
        self.input = url


    def process_url(self, url):
        # Reddit's unofficial API - add a '.json' suffix to any url
        if 'reddit.com' in url:
            return (url + '.json')

    def get_raw_content(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.5'
            }
        r = requests.get(url, headers=headers)
        return r.json()

    def current_timestamp(self):
        return datetime.timestamp(datetime.now())

    def get_thread(self, content):
        response_parent = content[0]['data']['children'][0]['data']
        response_comments = content[1]['data']['children']
        
        comments = {}
        
        def get_comments(comments_dict, path=[], depth_tracker=[]):
            for comment in comments_dict:
                id = comment['data']['name']
                replies = comment['data']['replies']
                parent_id = comment['data']['parent_id']
                is_submitter = 1 if comment['data']['is_submitter'] else 0
                depth = comment['data']['depth']
                depth_tracker.append(depth)
                print(depth_tracker)
                if len(depth_tracker) >= 2 and depth_tracker[-1] == depth_tracker[-2]:
                    path[-1] = id
                elif len(depth_tracker) >= 2 and depth_tracker[-1] < depth_tracker[-2]:
                    path = path[:depth+1]
                else:
                    path.append(id)
                
                '''
                if parent_id in comments.keys():
                    path = comments[parent_id]['parent_id'] + '/' + path
                if parent_id not in comments.keys():
                    path = comment['data']['parent_id'] + '/' + id
                '''
                comments.update({
                    id: {
                        'author': comment['data']['author'],
                        'text': comment['data']['body'],
                        'timestamp': comment['data']['created_utc'],
                        'permalink': comment['data']['permalink'],
                        'upvotes': comment['data']['ups'],
                        'downvotes': comment['data']['downs'],
                        'score': comment['data']['score'],
                        'parent_id': parent_id,
                        'ancestor_id': response_parent['name'],
                        'is_submitter': is_submitter,
                        'depth': comment['data']['depth'],
                        'path': '/'.join(path)
                        }
                    })
                if 'author_fullname' in comment['data'].keys():
                    comments[id]['author_id'] = comment['data']['author_fullname']
                else:
                    comments[id]['author_id'] = None
                print(f'Path: {path}')
                print(f"Depth: {comment['data']['depth']}")
                print(f'{"="*comments[id]["depth"]}>{id}: \n{comments[id]["text"]}\n\n')
                
                if len(replies) == 0:
                    continue
                else:
                    get_comments(replies['data']['children'], path, depth_tracker)
            
        get_comments(response_comments)

        parent_metadata = {
            'subreddit': response_parent['subreddit_name_prefixed'],
            'title': response_parent['title'],
            'timestamp': response_parent['created_utc'],
            'permalink': response_parent['permalink'],
            'num_comments': response_parent['num_comments'],
            'author': response_parent['author'],
            'upvotes': response_parent['ups'],
            'upvote_ratio': response_parent['upvote_ratio'],
            'downvotes': response_parent['downs'],
            'score': response_parent['score'],
            'id': response_parent['name'],
            'source': 'reddit'
        }

        if 'author_fullname' in response_parent.keys():
            parent_metadata['author_id'] = response_parent['author_fullname']
        else:
            parent_metadata['author_id'] = None

        thread = {
            'parent_metadata': parent_metadata,
            'timestamp': self.current_timestamp(),
            'comments': comments
        }
        return thread

    def main(self):
        return self.get_thread(self.get_raw_content(self.process_url(self.input)))

url = 'https://www.reddit.com/r/JuniorDoctorsUK/comments/uqzzz9/is_this_a_justified_reason_to_bleep_anaesthetic/'
def main():
    thread = Download(url).main()
    pprint.pprint(thread)

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(err)


