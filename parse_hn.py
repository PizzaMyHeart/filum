'''Parses the BeautifulSoup object created from the response from a
Hacker News item.

'''

from helpers import current_timestamp, bs4_to_md, iso_to_timestamp

def parse_hn(obj):
    soup = obj.soup
    parent = soup.find('table', class_='fatitem')
    parent_id = parent.find('tr', class_='athing').attrs['id']
    title = parent.find('a', class_='titlelink')
    score = None
    comments = soup.find_all('tr', class_='athing comtr')
    comment_data = {}

    def get_comment_text(item):
        comment_field = item.find('span', class_='commtext')
        #reply_span = comment_field.find('div', class_='reply')
        #reply_span.decompose()
        return bs4_to_md(comment_field)

    if title:            
        title = title.contents[0]
        score = parent.find('span', class_='score').contents[0]
        body = None
        parent_author = parent.find('td', class_='subtext').find('a', class_='hnuser').contents[0]
    else:
        # If the root item doesn't have a title element, then
        # it's a comment
        title = parent.find('span', class_='onstory').a.contents[0]
        body = get_comment_text(parent)
        parent_author = parent.find('a', class_='hnuser').contents[0]
    parent_timestamp = parent.find('span', class_='age').attrs['title']
    parent_timestamp = iso_to_timestamp(parent_timestamp)
    
    for comment in comments:
        depth = comment.find('td', class_='ind').attrs['indent']
        author = comment.find('a', class_='hnuser').contents[0]
        comment_id = comment.attrs['id']
        permalink = 'https://news.ycombinator.com/item?id=' + comment_id
        body = get_comment_text(comment)
        print(depth, author, permalink)
        print(body)
        print('------')
        comment_data.update({
            comment_id: {
                'author': author,
                'text': body,
                'permalink': permalink,
                'ancestor_id': parent_id,
                'depth': depth
            }
        })
    
    parent_data = {
        'title': title,
        'body': body,
        'author': parent_author,
        'id': parent_id,
        'score': score,
        'source': obj.site,
        'posted_timestamp': parent_timestamp,
        'saved_timestamp': current_timestamp()
    }

    thread = {
        'parent_data': parent_data,
        'comment_data': comment_data
    }

    return thread