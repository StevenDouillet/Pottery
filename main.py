import sqlite3

from flask import Flask, render_template, g

app = Flask(__name__)

DATABASE = 'database.db'

"""
#
# DATABASE
#
"""


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


"""
#
# ROUTES
#
"""


@app.route('/')
def root():
    cur = get_db().cursor()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM items')
        item_data = cur.fetchall()
    conn.close()
    items = parse(item_data)
    return render_template('index.html', title="Accueil", items=items)


"""
#
# PARSING DATABASE RESULTS
#
"""


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


if __name__ == '__main__':
    app.run(debug=True)
