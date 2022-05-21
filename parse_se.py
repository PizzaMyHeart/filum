'''Parses the BeautifulSoup object from the Stack Exchange page.
'''
from markdownify import markdownify as md

def parse_se(obj):
    soup = obj.soup.find(id='content')
    title = [string for string in soup.find(id='question-header').stripped_strings][0]
    permalink = soup.find(id='question-header').h1.a.get('href')
    question = soup.find(id='question')
    id = question.attrs['data-questionid']
    body = question.find('div', class_='s-prose js-post-body')
    body = md(str(body))
    def get_author(item):
        if item.find_all('div', class_='user-details')[-1].a:
            if item.find_all('div', class_='user-details')[-1].a.a:
                author = item.find_all('div', class_='user-details')[-1].a.a.string
            else:
                author = item.find_all('div', class_='user-details')[-1].a.string
        else:
            author = item.find_all('div', class_='user-details')[-1].span.string
        return author.strip()
    # The SE question author is last in the list of users on a question footer
    parent_author = get_author(question)
    print(parent_author)
    body = body.replace('\n', '')
    timestamp = soup.time.attrs['datetime']
    print(title, timestamp)
    print(body)
    print(permalink)

    answers = soup.find(id='answers')
    for answer in answers.find_all('div', class_='answer'):
        answer_id = answer.get('data-answerid')
        #print(answer_id)
        #print(answer)
        print('\n---')
        answer_author = get_author(answer)
        answer_timestamp = answer.time.attrs['datetime']
        #answer_author = answer.find_all('div', class_='user-info')[-1]
        print(answer_author)
        #print(answer_author, answer_timestamp)

    
