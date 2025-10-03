from flask import Flask, render_template, request, redirect, url_for
import sqlite3, uuid, requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
DB = 'portfolios.db'

# Инициализация БД
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE,
    name TEXT,
    bio TEXT,
    github TEXT,
    telegram TEXT,
    avatar TEXT,
    skills TEXT)''')
conn.commit()
conn.close()


def test_user():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''INSERT INTO portfolio (uuid, name, bio, github, telegram, avatar, skills)
                 VALUES ('23624', 'Rocket', 'Python Developer', 'rts-rocket', '@rocket_rts', 'mask.png', 'Python')''')
    conn.commit()
    conn.close()


@app.route('/')
def all_portfolios():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT uuid, name, avatar, bio FROM portfolio')
    portfolios = c.fetchall()
    conn.close()
    return render_template('all_portfolios.html', portfolios=portfolios)


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/generate', methods=['POST'])
def generate():
    form = request.form
    avatar = request.files.get('avatar')
    uid = str(uuid.uuid4())
    avatar_filename = ''

    if avatar and avatar.filename:
        filename = secure_filename(f"{uid}_{avatar.filename}")
        avatar_path = f"static/uploads/{filename}"
        avatar.save(avatar_path)
        avatar_filename = avatar_path.replace("static/", "")

    github = form['github'].strip().replace('https://github.com/', '').replace('/', '')

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''INSERT INTO portfolio (uuid, name, bio, github, telegram, avatar, skills)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (uid, form['name'], form['bio'], github, form['telegram'], avatar_filename, form['skills']))
    conn.commit()
    conn.close()

    return redirect(url_for('view_portfolio', uuid=uid))


@app.route('/portfolio/<uuid>')
def view_portfolio(uuid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT name, bio, github, telegram, avatar, skills FROM portfolio WHERE uuid = ?', (uuid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return "Портфолио не найдено", 404

    name, bio, github, telegram, avatar, skills_str = row
    skills = []
    for s in skills_str.split(','):
        skills.append(s.strip())

    projects = []
    try:
        r = requests.get(f"https://api.github.com/users/{github}/repos")
        if r.ok:
            for repo in r.json()[:6]:
                projects.append({
                    'title': repo['name'],
                    'description': repo.get('description') or 'Без описания',
                    'link': repo['html_url']
                })
    except Exception as e:
        print("GitHub API error:", e)

    tool_icons = {
        "Python": "🐍", "Flask": "🌶", "HTML": "📄", "CSS": "🎨",
        "HTML/CSS": "🖌️", "Git": "🔧", "GitHub": "🐙", "Telegram": "✈️",
        "Телеграм": "✈️", "SQL": "🗄️", "SQLite": "📘", "JavaScript": "⚡",
        "JS": "⚡", "Jinja": "🧩"
    }

    return render_template(
        "portfolio_template.html",
        name=name,
        bio=bio,
        github=github,
        telegram=telegram,
        avatar=avatar,
        skills=skills,
        projects=projects,
        tool_icons=tool_icons
    )


if __name__ == '__main__':
    app.run(debug=True)