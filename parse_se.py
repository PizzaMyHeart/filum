'''Parses the BeautifulSoup object from a Stack Exchange page.
'''
from markdownify import markdownify as md
from helpers import root_url, current_timestamp

def parse_se(obj):
    soup = obj.soup.find(id='content')
    if '#' in obj.url:
        print(obj.url)
        root_is_answer = True
        answer_id = obj.url.split('#')[-1]
        print('answer_id: ' + answer_id)
    url = root_url(obj.url)
    title = [string for string in soup.find(id='question-header').stripped_strings][0]
    question_permalink = url + soup.find(id='question-header').h1.a.get('href')
    question = soup.find(id='question')
    question_score = question.get('data-score')
    question_id = question.attrs['data-questionid']
    children = {}
        
    def get_body(item):
        body = item.find('div', class_='s-prose js-post-body')
        body = md(str(body))
        body = body.replace('\n', '')
        return body
    def get_author(item):
        # The SE question author is last in the list of users on a question footer
        if item.find_all('div', class_='user-details')[-1].a:
            if item.find_all('div', class_='user-details')[-1].a.a:
                author = item.find_all('div', class_='user-details')[-1].a.a.string
            else:
                author = item.find_all('div', class_='user-details')[-1].a.string
        else:
            author = item.find_all('div', class_='user-details')[-1].span.string
        return author.strip()
    question_body = get_body(question)
    question_author = get_author(question)
    
    question_timestamp = soup.time.attrs['datetime']
    print(title, question_timestamp, question_score)
    print(question_body)

    parent_data = {
    'title': title,
    'body': question_body,
    'author': question_author,
    'id': question_id,
    'score': question_score,
    'permalink': question_permalink,
    'source': obj.site
    }

    if root_is_answer:
        answers = soup.find_all(id=f'answer-{answer_id}')
    else:
        answers = soup.find(id='answers').find_all('div', class_='answer')
    
        
    for answer in answers:
        answer_id = answer.get('data-answerid')
        answer_score = answer.get('data-score')
        answer_body = get_body(answer)
        print('\n---')
        answer_author = get_author(answer)
        answer_timestamp = answer.time.attrs['datetime']
        answer_permalink = url + 'a/' + answer_id        
        print(answer_author, answer_score)
        print(answer_body, answer_timestamp)

        children.update({
            answer_id:{
                'author': question_author,
                'text': answer_body,
                'ancestor_id': question_id,
                'depth': 1,
                'score': answer_score,
                'timestamp': answer_timestamp,
                'permalink': answer_permalink
            }
        })

        comments = answer.find_all('li', class_='comment')
        
        if len(comments) == 0:
            continue
        for comment in comments:
            comment_id = comment.get('data-comment-id')
            comment_score = comment.get('data-comment-score')
            comment_body = md(str(comment.find('span', class_='comment-copy'))).replace('\n', '')
            comment_author = comment.select('.comment-user')[0].string
            comment_timestamp = comment.find('span', class_='relativetime-clean').attrs['title'].split('Z')[0]
            print(comment_id, comment_author, comment_score)
            print(comment_body, comment_timestamp)

            children.update({
                comment_id:{
                    'author': comment_author,
                    'text': comment_body,
                    'ancestor_id': question_id,
                    'depth': 2,
                    'score': comment_score
                }
            })
    thread = {
        'parent_data': parent_data,
        'comment_data': children,
        'timestamp': current_timestamp()
    }

    return thread
    
