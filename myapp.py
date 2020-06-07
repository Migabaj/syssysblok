from flask import Flask, render_template
import sqlite3
from pprint import pprint

app = Flask(__name__)


@app.route('/')
def index():
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles")
    global articles_db
    articles_db = c.fetchall()
    conn.close()

    articles = []
    articles_db_slice = articles_db
    while articles_db_slice:
        articles.append(articles_db_slice[:3])
        articles_db_slice = articles_db_slice[3:]
    return render_template('index.html', articles=articles)


@app.route(f'/articles/<i>.html')
def article_path(i):
    return render_template(f'articles/{i}.html', article=articles_db[int(i)])


@app.route('/generate')
def generate():
    import markovify
    import random
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute("SELECT * FROM articles")
    article_html = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <title>
                    ССБъ
                </title>
                <meta charset="utf-8">
                <link rel="stylesheet" type="text/css" href="../../static/style.css?q=7">
            </head>
            <body>
                <div class="header">
                    <span>
                      <a href="/">
                        СИСТЕМНЫЙ СИСТЕМНЫЙ БЛОК{Ъ}
                      </a>
                    </span>
                    <span class="more">
                      <a href="generate.html">
                        СГЕНЕРИРОВАТЬ СТАТЬЮ
                      </a>
                    </span>
                </div>
                <div class="content-with-heading">
                    <h1 class="heading">
                        {{article[1]}}
                    </h1>
                <div class="art-text">
                    {% for par in article[2].split("\n") %}
                        <p>{{par}}</p><br>
                    {% endfor %}
                </div>
                </div>
            </body>    
            """
    model = markovify.Text.from_json(open("models/corpus.json").read())
    art = ""
    for i in range(3):
        paragraph = ""
        for j in range(random.randint(1, 3)):
            for k in range(random.randint(1, 10)):
                sent = None
                while not sent:
                    sent = model.make_short_sentence(280)
                    paragraph += " " + sent
        art += paragraph + "\n"
    heading = None
    while not heading:
        heading = model.make_short_sentence(60)
    art_attributes = (heading.strip('.'), art)
    conn = sqlite3.connect('articles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles")
    all_articles = c.fetchall()
    c.execute("INSERT INTO articles VALUES (?, ?, ?)", (len(all_articles),
                                                        art_attributes[0],
                                                        art_attributes[1]))
    conn.commit()
    conn.close()
    with open(f"templates/articles/{len(all_articles)}.html", "w", encoding="utf-8") as f:
        f.write(article_html)
    return render_template(f"articles/{len(all_articles)}.html", article=(len(all_articles), art_attributes[0], art_attributes[1]))


if __name__ == '__main__':
    app.run(debug=False)
