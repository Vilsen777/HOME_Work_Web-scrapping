import requests
from bs4 import BeautifulSoup

# Ключевые слова для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# Ссылка на страницу со статьями
URL = 'https://habr.com/ru/articles/'

# Заголовки запроса
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


def get_response(url):
    """Отправляет GET-запрос и возвращает ответ сервера."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response


def get_articles(html):
    """Возвращает все карточки статей со страницы."""
    soup = BeautifulSoup(html, 'lxml')
    return soup.find_all('article')


def contains_keywords(text, keywords):
    """Проверяет, есть ли в тексте хотя бы одно ключевое слово."""
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)


def extract_article_data(article):
    """Извлекает дату, заголовок, ссылку и preview-текст статьи."""
    h2_tag = article.find('h2')
    if h2_tag is None:
        return None

    a_tag = h2_tag.find('a')
    if a_tag is None:
        return None

    title = a_tag.get_text(strip=True)

    href = a_tag.get('href')
    if not href:
        return None
    link = href if href.startswith('http') else f'https://habr.com{href}'

    time_tag = article.find('time')
    date = time_tag.get('datetime', '').split('T')[0] if time_tag else 'Дата не найдена'

    preview_paragraphs = article.find_all('p')
    preview_text = ' '.join(
        p.get_text(" ", strip=True) for p in preview_paragraphs
    )

    searchable_text = f'{title} {preview_text}'

    return {
        'date': date,
        'title': title,
        'link': link,
        'searchable_text': searchable_text
    }


def main():
    try:
        response = get_response(URL)
        articles = get_articles(response.text)

        for article in articles:
            article_data = extract_article_data(article)

            if article_data is None:
                continue

            if contains_keywords(article_data['searchable_text'], KEYWORDS):
                print(f"<{article_data['date']}> - <{article_data['title']}> - <{article_data['link']}>")

    except requests.exceptions.RequestException as error:
        print(f'Ошибка при выполнении запроса: {error}')


if __name__ == '__main__':
    main()