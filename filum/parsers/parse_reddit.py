from filum.helpers import html_to_md, current_timestamp


def parse_reddit(obj):
    content = obj.r
    parent = content[0]['data']['children'][0]['data']
    comments = content[1]['data']['children']

    comment_data = {}

    def get_comments(comments_dict):
        for comment in comments_dict:
            id = comment['data']['name']  # Used as dict key for comments
            if comment['kind'] == 'more':
                # These are comments that are hidden under the fold. There is usually a link saying
                # '_load more comments_'
                # TODO: Rewrite reddit parser to hit new URL and retrieve unexpanded children
                # Depth will need to be checked programmatically.
                continue

            parent_id = comment['data']['parent_id']
            depth = comment['data']['depth']
            replies = comment['data']['replies']

            comment_body = comment['data']['body_html']
            comment_body = html_to_md(comment_body)
            comment_permalink = f'https://reddit.com{comment["data"]["permalink"]}'
            comment_data.update({
                id: {
                    'author': comment['data']['author'],
                    'text': comment_body,
                    'timestamp': comment['data']['created_utc'],
                    'permalink': comment_permalink,
                    'upvotes': comment['data']['ups'],
                    'downvotes': comment['data']['downs'],
                    'score': comment['data']['score'],
                    'parent_id': parent_id,
                    'ancestor_id': parent['name'],
                    'depth': depth
                    }
                })
            if 'author_fullname' in comment['data'].keys():
                comment_data[id]['author_id'] = comment['data']['author_fullname']
            else:
                comment_data[id]['author_id'] = None

            if len(replies) == 0:
                continue
            else:
                get_comments(replies['data']['children'])

    get_comments(comments)
    body = html_to_md(parent['selftext_html']) if parent['selftext_html'] else None
    parent_permalink = f'https://www.reddit.com{parent["permalink"]}'  # The 'www' part is important
    parent_metadata = {
        'title': parent['title'],
        'body': body,
        'permalink': parent_permalink,
        'num_comments': parent['num_comments'],
        'author': parent['author'],
        'score': parent['score'],
        'id': parent['name'],
        'source': obj.site,
        'posted_timestamp': parent['created_utc'],
        'saved_timestamp': current_timestamp()
    }

    thread = {
        'parent_data': parent_metadata,
        'comment_data': comment_data
    }

    print(thread)
    print('\n====\n')
    return thread
