# WizBlog
A simple framework for a blog.

## Installation
Download, install the python prerequisited, and copy / edit the config:

```bash
$ git clone https://github.com/WizBoom/WizBlog.git
$ cd WizBlog
$ virtualenv -p python3.6 env
$ . env/bin/activate
$ pip install -r requirements.txt
$ cp config.json.example config.json
```

Edit config.json file.

## Database.
If you do not have the correct database yet:

```bash
$ python create_database.py
```

## Running

```bash
$ sh gunicorn_run.sh
```
