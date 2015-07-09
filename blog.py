import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define,options,parse_command_line
import MySQLdb
import MySQLdb.cursors
import time

define('port',default=8000,help='run on the given port',type=int)
define("debug", default=True, help="run in debug mode")


class App(tornado.web.Application):
    def __init__(self):
        handlers=[
            (r'/',MainHandler),
            (r'/page/(\d+)',MainHandler),
            (r'/blog',BlogHandler),
            (r'/login',LoginHandler),
            
        ]
        settings=dict(
            template_path=os.path.join(os.path.dirname(__file__),'template'),
            static_path=os.path.join(os.path.dirname(__file__),'static'),
            debug=options.debug,

            )
        try:
            conn=MySQLdb.connect(host='localhost',user='root',passwd='123456a',cursorclass=MySQLdb.cursors.DictCursor)
            conn.select_db('blog')
            self.cur=conn.cursor()

        except MySQLdb.Error,e:
            print 'Mysql Error %s'%e
        tornado.web.Application.__init__(self,handlers,**settings)

class MainHandler(tornado.web.RequestHandler):

    def get(self,page=None):
        self.application.cur.execute('select * from passage order by id desc')
        passage=self.application.cur.fetchall()
        if len(passage)==0:
            pages=1
        elif len(passage)%3==0:
            pages=len(passage)/3
        else:
            pages=len(passage)/3+1
        if page: 
            start=(int(page)-1)*3
            
            self.application.cur.execute('select * from passage order by id desc limit %s,3',start)
            passage=self.application.cur.fetchall()

            self.render('index.html',passage=passage,page=int(page),pages=pages)
        else:
            self.application.cur.execute('select * from passage order by id desc limit 0,3 ')
            passage=self.application.cur.fetchall()

            self.render('index.html',passage=passage,page=1,pages=pages)


    

class BlogHandler(tornado.web.RequestHandler):
    def get(self):

        self.render('post.html')
    def post(self):
        p_date=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        title=self.get_argument('title').encode('utf-8')
        author=self.get_argument('author').encode('utf-8')
        content=self.get_argument('context').encode('utf-8')
        url=self.get_argument('url').encode('utf-8')
        cat=self.get_argument('cat').encode('utf-8')
        cat_url=self.get_argument('cat_url').encode('utf-8')
        try:
            self.application.cur.execute("insert into passage(title,author,p_date,content,cat,url,cat_url)values(%s,%s,%s,%s,%s,%s,%s)",(title,author,p_date,content,cat,url,cat_url))
            self.redirect('/')
        except:
            self.write('Something goes wrong')
   
        #self.redirect('/')
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('login.html')
    def post(self):
        user=self.get_argument('username')
        passwd=self.get_argument('passwd')
        self.application.cur.execute("select * from user where username=%s and passwd=%s",(user,passwd))
        login=self.application.cur.fetchall()
        if len(login)==1:
            self.redirect('/blog')
        else:
            self.render('login.html')

def main():
    parse_command_line()
    app = App()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__=='__main__':
	main()