from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import hashlib
import xml.etree.ElementTree as ET
import os
import subprocess
import tempfile

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create data directory if it doesn't exist
data_dir = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

users_file = os.path.join(data_dir, 'users.xml')
diary_file = os.path.join(data_dir, 'diary.xml')
schema_file = os.path.join(data_dir, 'schema.xsd')
transform_file = os.path.join(data_dir, 'transform.xslt')

users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_users():
    root = ET.Element('users')
    for username, password in users.items():
        user_elem = ET.SubElement(root, 'user')
        ET.SubElement(user_elem, 'username').text = username
        ET.SubElement(user_elem, 'password').text = password

    tree = ET.ElementTree(root)
    tree.write(users_file)

def load_users():
    if os.path.exists(users_file):
        tree = ET.parse(users_file)
        root = tree.getroot()
        for user_elem in root.findall('user'):
            username = user_elem.find('username').text
            password = user_elem.find('password').text
            users[username] = password

load_users()

# Create diary file if it doesn't exist
if not os.path.exists(diary_file):
    with open(diary_file, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?><diary></diary>')

def add_entry(username, title, content):
    tree = ET.parse(diary_file)
    root = tree.getroot()

    user = root.find(f"./user[@username='{username}']")
    if user is None:
        user = ET.SubElement(root, 'user', username=username)

    entry = ET.SubElement(user, 'entry')
    ET.SubElement(entry, 'title').text = title
    ET.SubElement(entry, 'content').text = content

    tree.write(diary_file)

def get_entries(username):
    tree = ET.parse(diary_file)
    root = tree.getroot()

    user = root.find(f"./user[@username='{username}']")
    if user is None:
        return []

    entries = []
    for entry in user.findall('entry'):
        title = entry.find('title').text
        content = entry.find('content').text
        entries.append({'title': title, 'content': content})

    return entries

def delete_entry(username, title):
    tree = ET.parse(diary_file)
    root = tree.getroot()

    user = root.find(f"./user[@username='{username}']")
    if user is None:
        return False

    entry = user.find(f"./entry[title='{title}']")
    if entry is None:
        return False

    user.remove(entry)
    tree.write(diary_file)
    return True

def update_entry(username, old_title, new_title, new_content):
    tree = ET.parse(diary_file)
    root = tree.getroot()

    user = root.find(f"./user[@username='{username}']")
    if user is None:
        return False

    entry = user.find(f"./entry[title='{old_title}']")
    if entry is None:
        return False

    entry.find('title').text = new_title
    entry.find('content').text = new_content
    tree.write(diary_file)
    return True

def validate_xml(xml_content, schema_path):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(xml_content.encode('utf-8'))
            temp_file_path = temp_file.name

        result = subprocess.run(['java', 'XMLValidator', schema_path, temp_file_path], capture_output=True, text=True)
        os.remove(temp_file_path)
        return 'XML is valid: true' in result.stdout
    except Exception as e:
        print(e)
        return False

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('diary'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        if username in users:
            return 'User already exists!'
        users[username] = password
        save_users()
        session['username'] = username
        return redirect(url_for('diary'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        if username not in users or users[username] != password:
            return 'Invalid username or password'
        session['username'] = username
        return redirect(url_for('diary'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        entry_id = request.form.get('entryId')
        title = request.form['title']
        content = request.form['content']

        # Construct a temporary XML string
        temp_xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
        <diary>
            <user username="{session['username']}">
                <entry>
                    <title>{title}</title>
                    <content>{content}</content>
                </entry>
            </user>
        </diary>'''

        if not validate_xml(temp_xml_content, schema_file):
            return 'Invalid XML format!', 400

        if entry_id:
            entries = get_entries(session['username'])
            old_title = entries[int(entry_id)]['title']
            updated = update_entry(session['username'], old_title, title, content)
        else:
            add_entry(session['username'], title, content)
        return redirect(url_for('diary'))

    entries = get_entries(session['username'])
    return render_template('diary.html', entries=entries)

@app.route('/edit_entry/<title>', methods=['GET', 'POST'])
def edit_entry(title):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        entries = get_entries(session['username'])
        entry = next((e for e in entries if e['title'] == title), None)
        if not entry:
            return jsonify({'error': 'Entry not found or you are not authorized to edit it'}), 404

        return jsonify(entry)

    if request.method == 'POST':
        new_title = request.json.get('title')
        new_content = request.json.get('content')
        updated = update_entry(session['username'], title, new_title, new_content)
        if updated:
            return jsonify({'message': 'Entry updated successfully'})
        else:
            return jsonify({'error': 'Error updating entry'}), 500

@app.route('/delete_entry_route/<title>', methods=['POST'])
def delete_entry_route(title):
    if 'username' not in session:
        return redirect(url_for('login'))

    deleted = delete_entry(session['username'], title)
    if deleted:
        return jsonify({'message': 'Entry deleted successfully'})
    else:
        return jsonify({'error': 'Error deleting entry'}), 500

if __name__ == '__main__':
    app.run(debug=True)
