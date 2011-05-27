
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson

import os

class Todos(db.Model):
    order = db.IntegerProperty()
    content = db.StringProperty()
    done = db.BooleanProperty()

    def toDict(self):
	todo = {
	    'id': self.key().id(), 
	    'order': self.order,
	    'content': self.content,
	    'done': self.done
	    }
	return todo

class MainHandler(webapp.RequestHandler):
    def get(self):
	path = os.path.join(os.path.dirname(__file__), 'index.html')
	self.response.out.write(template.render(path, None))	

class RESTfulHandler(webapp.RequestHandler):
    def get(self):
	todos = []
	query = Todos.all()
	for todo in query:
	    todos.append(todo.toDict())
	todos = simplejson.dumps(todos)
	self.response.out.write(todos)

    def post(self):
	todo = simplejson.loads(self.request.body)
	todo = Todos(order   = todo['order'],
		     content = todo['content'],
		     done    = todo['done'])
	todo.put()
	todo = simplejson.dumps(todo.toDict())
	self.response.out.write(todo)

    def put(self, id):
	tmp = simplejson.loads(self.request.body)
	todo = Todos.get_by_id(int(id))
	todo.content = tmp['content']
	todo.done    = tmp['done']
	todo.put()
	todo = simplejson.dumps(todo.toDict())
	self.response.out.write(todo)

    def delete(self, id):
	todo = Todos.get_by_id(int(id))
	tmp = todo.toDict()
	todo.delete()
	todo = simplejson.dumps(tmp)
	#self.response.write.out(todo)
	
application = webapp.WSGIApplication(
				     [('/', MainHandler),
				      ('/todos', RESTfulHandler),
				      ('/todos/([0-9]*)', RESTfulHandler)],
				      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


