from app import db
from datetime import datetime

class Entry(db.Model):

	__tablename__ = "blog_entries"

	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime)
	title = db.Column(db.String)
	shortDesc = db.Column(db.String)
	content = db.Column(db.String)
	published = db.Column(db.Boolean)

	def __init__(self,title,shortDesc,content,published):
		self.timestamp = datetime.utcnow()
		self.title = title
		self.shortDesc = shortDesc
		self.content = content
		self.published = published

	def __repr__(self):
		return '{} posted at {} with id {}'.format(self.title,self.timestamp,self.id)