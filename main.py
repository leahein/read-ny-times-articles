'''Display a NYT article in the browser'''

import sys
import tempfile
import webbrowser

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore

BASIC_STYLING = '''
<style>
body {
    font-family: sans-serif;
    color: #222;
}
h1, h2, h3 {
    margin: 0.65em;
}

h1 {
    font-size: 30px;
}

h2 {
    font-size: 25px;
}

h3 {
    font-size: 20px;
}
p {
    margin: 0 0 1.15em;
}
.StoryBodyCompanionColumn {
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
    padding: 24px;
}
</style>
'''


def render_file(title: Tag, text: Tag):
    '''Renders the given title and text to a temp file and opens the file

    The title and text are formatted with the appropriate HTML tags.
    File is rendered in the default browser.
    '''
    with tempfile.NamedTemporaryFile(delete=False) as file_obj:
        file_obj.write(
            f'''
            <head>
                {BASIC_STYLING}
                {title}
            </head>
        '''.encode()
        )
        file_obj.write(
            f'''
            <body>
                <h1>{title.string}</h1>
                <div>{text}</div>
            </body>
            '''.encode()
        )
        file_obj.seek(0)

        filename = f'file://{file_obj.name}'
        webbrowser.open(filename)


def parse_article(article: str) -> tuple[Tag, Tag]:
    '''Parse the given NYT article for the title and relevant text'''

    html = BeautifulSoup(article, 'html.parser')

    body: Tag = html.find(attrs={'name': 'articleBody'})
    content: list[Tag] = body.find_all('div', class_='StoryBodyCompanionColumn')
    content_str = '\n'.join(str(section) for section in content)

    return html.title, content_str


def get_article(url: str) -> str:
    '''Get a NYT article'''
    resp = requests.get(url, headers={'User-Agent': 'curl/7.83.1'})
    resp.raise_for_status()
    return resp.text


def main(url: str):
    '''Main function'''

    article = get_article(url)
    title, text = parse_article(article)
    render_file(title, text)
    print('Enjoy 🤓')


if __name__ == '__main__':
    try:
        [_, url_] = sys.argv  # pylint: disable=unbalanced-tuple-unpacking
    except ValueError:
        print('Please pass in the URL of the NYT article')
        raise

    main(url_)
