import requests
import re
import pprint
from bs4 import BeautifulSoup
import traceback
from parse_hn import parse_hn
from parse_se import parse_se
from helpers import current_timestamp, html_to_md

class Download:
    def __init__(self, url):
        self.url = url
        return

    def process_url(self):
        # Reddit's unofficial API - add a '.json' suffix to any url
        if 'reddit.com' in self.url:
            self.url += '.json'
            self.site = 'reddit'
        elif 'news.ycombinator.com' in self.url:
            self.site = 'hn'
        elif 'stackexchange.com' in self.url or 'stackoverflow.com' in self.url:
            self.site = 'se'
        print(self.site)
        return self

    def get_response(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.5'
            }
        self.r = requests.get(self.url, headers=headers)
        return self

    def parse_html(self, raw):
        self.soup = BeautifulSoup(raw, 'html.parser')
        return self
    
    def prepare_response(self):
        print(self.site)
        if self.site == 'reddit':
            self.r = self.r.json()
        else:
            self.r = self.parse_html(self.r.text)
        return self

    
        

    def parse_reddit(self):
        content = self.r
        print(content)
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
                #print(depth_tracker)
                if len(depth_tracker) >= 2 and depth_tracker[-1] == depth_tracker[-2]:
                    path[-1] = id
                elif len(depth_tracker) >= 2 and depth_tracker[-1] < depth_tracker[-2]:
                    path = path[:depth+1]
                else:
                    path.append(id)
                

                comments.update({
                    id: {
                        'author': comment['data']['author'],
                        'text': html_to_md(comment['data']['body_html']),
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
                
                if len(replies) == 0:
                    continue
                else:
                    get_comments(replies['data']['children'], path, depth_tracker)
            
        get_comments(response_comments)
        body = response_parent['selftext_html'] if response_parent['selftext_html'] else None
        parent_metadata = {
            'title': response_parent['title'],
            'body': html_to_md(body),
            'timestamp': response_parent['created_utc'],
            'permalink': response_parent['permalink'],
            'num_comments': response_parent['num_comments'],
            'author': response_parent['author'],
            'score': response_parent['score'],
            'id': response_parent['name'],
            'source': self.site
        }

        thread = {
            'parent_data': parent_metadata,
            'timestamp': current_timestamp(),
            'comment_data': comments
        }
        return thread
    
    
    
    def get_thread(self):
        if self.site == 'reddit':
            return self.parse_reddit()
        elif self.site == 'hn':
            return parse_hn(self)
        elif self.site == 'se':
            return parse_se(self)

    def run(self):
        return self.process_url().get_response().prepare_response().get_thread()
        

hn_url_root = 'https://news.ycombinator.com/item?id=31447804'
hn_url_comment = 'https://news.ycombinator.com/item?id=31451536'
se_url_root = 'https://stats.stackexchange.com/questions/6/the-two-cultures-statistics-vs-machine-learning'
se_url_answer = 'https://stackoverflow.com/questions/15340582/python-extract-pattern-matches/15340666#15340666'
reddit_url_root = 'https://www.reddit.com/r/boardgames/comments/utkslk/tiny_epic_which_one_would_you_recommend/'

def main():
    Download(reddit_url_root).process_url().get_response().prepare_response().get_thread()
    

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        traceback.print_exc()


