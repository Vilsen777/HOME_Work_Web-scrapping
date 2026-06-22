import requests
from bs4 import BeautifulSoup

# Ключевые слова для поиска
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# Адрес страницы со свежими статьями
URL = 'https://habr.com/ru/articles/'

# Заголовки запроса: User-Agent помогает получить страницу корректно
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


def get_response(url):
    """Отправляет GET-запрос и возвращает объект ответа."""
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response


def parse_articles(html):
    """Находит все статьи на странице и возвращает список тегов article."""
    soup = BeautifulSoup(html, 'lxml')
    return soup.find_all('article')


def extract_article_data(article):
    """
    Извлекает данные одной статьи:
    дату, заголовок, ссылку и preview-текст.
    """
    h2_tag = article.find('h2')
    if h2_tag is None:
        return None

    a_tag = h2_tag.find('a')
    if a_tag is None:
        return None

    title = a_tag.text.strip()

    href = a_tag.get('href')
    if not href:
        return None

    # Если ссылка относительная, добавляем домен
    link = href if href.startswith('http') else f'https://habr.com{href}'

    time_tag = article.find('time')
    if time_tag is not None:
        date = time_tag.get('datetime', '').split('T')[0]
    else:
        date = 'Дата не найдена'

    # Берём весь текст карточки статьи, доступный на текущей странице
    preview_text = article.get_text(separator=' ', strip=True).lower()

    return {
        'date': date,
        'title': title,
        'link': link,
        'preview_text': preview_text
    }


def contains_keywords(text, keywords):
    """Проверяет, есть ли в тексте хотя бы одно ключевое слово."""
    for keyword in keywords:
        if keyword.lower() in text:
            return True
    return False


def main():
    try:
        response = get_response(URL)
        articles = parse_articles(response.text)

        for article in articles:
            article_data = extract_article_data(article)

            if article_data is None:
                continue

            if contains_keywords(article_data['preview_text'], KEYWORDS):
                print(f"<{article_data['date']}> - <{article_data['title']}> - <{article_data['link']}>")

    except requests.exceptions.RequestException as error:
        print(f'Ошибка при выполнении запроса: {error}')


if __name__ == '__main__':
    main()