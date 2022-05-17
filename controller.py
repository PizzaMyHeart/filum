from models import Model_db
from download import Download
import pprint
import traceback
url = 'https://www.reddit.com/r/JuniorDoctorsUK/comments/urj5fk/for_those_looking_at_positions_abroad_new_zealand/'

class Controller(object):
    def __init__(self, model):
        self.model = model
        self.downloaded_thread = Download(url).main()

    def add_thread(self, values, table_name):
        try:
            self.model.insert_row(values, table_name)
        except Exception as err:
            traceback.print_exc()


def main():
    c = Controller(Model_db())
    thread = c.downloaded_thread
    values = (
        thread['parent_metadata']['id'], 
        thread['parent_metadata']['title'],
        thread['parent_metadata']['timestamp'],
        thread['parent_metadata']['permalink'],
        thread['parent_metadata']['num_comments'],
        thread['parent_metadata']['author'],
        thread['parent_metadata']['source']
        )
    c.add_thread([values], 'ancestors')
    comments = []
    for comment in thread['comments'].values():
        comments.append((
            comment['ancestor_id'],
            comment['author'],
            comment['author_id'],
            comment['depth'],
            comment['downvotes'],
            comment['is_submitter'],
            comment['parent_id'],
            comment['path'],
            comment['permalink'],
            comment['score'],
            comment['text'],
            comment['timestamp'],
            comment['upvotes']
        ))
    #pprint.pprint(comments)
    c.add_thread(comments, 'descendants')      

        

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        traceback.print_exc()
