
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson

from datetime import datetime
import os, Cookie

class TodoList(db.Model):
    timestamp = db.DateTimeProperty(auto_now_add=True)

class Todos(db.Model):
    todolist = db.ReferenceProperty(TodoList)
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
	if self.request.cookies.get('todos', None) == None:
	    todolist = TodoList()
	    todolist.put()
	    cookie = Cookie.SimpleCookie()
	    cookie['todos'] = todolist.key().__str__()
	    cookie['todos']['expires'] = datetime(2014, 1, 1).strftime('%a, %d %b %Y %H:%M:%S')
	    cookie['todos']['path'] = '/'
	    self.response.headers.add_header('Set-Cookie', cookie['todos'].OutputString())
	path = os.path.join(os.path.dirname(__file__), 'index.html')
	self.response.out.write(template.render(path, None))

class RESTfulHandler(webapp.RequestHandler):
    def get(self, id):
	key = self.request.cookies['todos']
	todolist = db.get(key)
	todos = []
	query = Todos.all()
	query.filter("todolist =", todolist.key())
	for todo in query:
	    todos.append(todo.toDict())
	todos = simplejson.dumps(todos)
	self.response.out.write(todos)

    def post(self, id):
	key = self.request.cookies['todos']
	todolist = db.get(key)
	todo = simplejson.loads(self.request.body)
	todo = Todos(todolist = todolist.key(),
		     order   = todo['order'],
		     content = todo['content'],
		     done    = todo['done'])
	todo.put()
	todo = simplejson.dumps(todo.toDict())
	self.response.out.write(todo)

    def put(self, id):
	key = self.request.cookies['todos']
	todolist = db.get(key)
	todo = Todos.get_by_id(int(id))
	if todo.todolist.key() == todolist.key():
	    tmp = simplejson.loads(self.request.body)
	    todo.content = tmp['content']
	    todo.done    = tmp['done']
	    todo.put()
	    todo = simplejson.dumps(todo.toDict())
	    self.response.out.write(todo)
	else:
	    self.error(403)

    def delete(self, id):
	key = self.request.cookies['todos']
        todolist = db.get(key)
	todo = Todos.get_by_id(int(id))
	if todo.todolist.key() == todolist.key():
	    tmp = todo.toDict()
	    todo.delete()
	else:
	    self.error(403)
	
application = webapp.WSGIApplication(
				     [('/', MainHandler),
				      ('/todos\/?([0-9]*)', RESTfulHandler)],
				      debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()


