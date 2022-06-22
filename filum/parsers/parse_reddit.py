from filum.helpers import add_comment_author_to_title, html_to_md, current_timestamp


def parse_reddit(json, site, item_permalink):
    content = json
    parent = content[0]['data']['children'][0]['data']
    comments = content[1]['data']['children']

    comment_data = {}
    body = html_to_md(html_to_md(parent['selftext_html'])) if parent['selftext_html'] else None
    parent_permalink = f'https://www.reddit.com{parent["permalink"]}'  # The 'www' part is important
    title = parent['title']
    author = parent['author']
    parent_id = parent['name']
    score = parent['score']
    if len(comments) == 1:
        # For cases when the user intends to save a specific comment rather than the
        # whole thread.
        # The JSON object returned from a child permalink (as opposed to the root)
        # contains only one item in [0][data][children].
        title = add_comment_author_to_title(comments[0]['data']['author'], title)
        parent_id = comments[0]['data']['id']
        score = comments[0]['data']['score']

    def get_comments(comments: dict):
        for comment in comments:
            id = comment['data']['name']  # Used as dict key for comments
            if comment['kind'] == 'more':
                # These are comments that are hidden under the fold. There is usually a link saying
                # '_load more comments_'
                # TODO: Rewrite reddit parser to hit new URL and retrieve unexpanded children
                # Depth will need to be checked programmatically.
                continue

            depth = comment['data']['depth']
            replies = comment['data']['replies']

            comment_body = comment['data']['body_html']
            # Unclear to me why Reddit post and comment text need to be passed through
            # html_to_md twice.
            comment_body = html_to_md(html_to_md(comment_body))
            comment_permalink = f'https://reddit.com{comment["data"]["permalink"]}'
            comment_data.update({
                id: {
                    'author': comment['data']['author'],
                    'text': comment_body,
                    # 'ancestor_id': parent['name'],
                    'ancestor_id': parent_id,
                    'depth': depth,
                    'score': comment['data']['score'],
                    'timestamp': comment['data']['created_utc'],
                    'permalink': comment_permalink,
                    }
                })
            if 'author_fullname' in comment['data'].keys():
                comment_data[id]['author_id'] = comment['data']['author_fullname']
            else:
                comment_data[id]['author_id'] = ''

            if len(replies) == 0:
                continue
            else:
                get_comments(replies['data']['children'])
    get_comments(comments)
    parent_data = {
        'title': title,
        'body': body,
        'author': author,
        'id': parent_id,
        'score': score,
        'item_permalink': item_permalink,
        'parent_permalink': parent_permalink,
        'source': site,
        'posted_timestamp': parent['created_utc'],
        'saved_timestamp': current_timestamp()
    }

    thread = {
        'parent_data': parent_data,
        'comment_data': comment_data
    }
    return thread
