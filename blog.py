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
define('mysql_host',default='localhost',help='mysql host address')
define('mysql_db',default='blog',help='mysql database name')
define('mysql_user',default='root',help='mysql username')
define('mysql_pwd',default='123456a',help='mysql user password')
define('mysql_charset',default='utf8',help='mysql charset')



class Application(tornado.web.Application):
    def __init__(self):
        handlers=[
            (r'/',MainHandler),
            (r'/page/(\d+)',MainHandler),
            (r'/blog',BlogHandler),
            (r'/login',LoginHandler),
            (r'/single/([% _ \- \wd]+)',SingleHandler),
            (r'/cat/([% _ \- \wd]+)',CatHandler),
            (r'/quit',QuitHandler),
            (r'/edit-cat',EditCatHandler),
            
        ]
        settings=dict(
            template_path=os.path.join(os.path.dirname(__file__),'template'),
            static_path=os.path.join(os.path.dirname(__file__),'static'),
            debug=options.debug,
            ui_modules={'nav':NavModule,'entry':EntryModule,'headernav':HeaderNavModule,'sidebar':SidebarModule},
            cookie_secret='123456a',


            )

        try:
            conn=MySQLdb.connect(
                host=options.mysql_host,user=options.mysql_user,
                passwd=options.mysql_pwd,db=options.mysql_db,
                charset=options.mysql_charset,
                cursorclass=MySQLdb.cursors.DictCursor
                )
            
            self.cur=conn.cursor()

        except MySQLdb.Error,e:
            print 'Mysql Error %s'%e

        tornado.web.Application.__init__(self,handlers,**settings)

class BaseHandler(tornado.web.RequestHandler):
    @property
    def cur(self):
        return self.application.cur

    def is_login(self):
        
        my_cookie=self.get_secure_cookie('cookie_name')
        if my_cookie=='':
            return False
        else:
            return True

    

class MainHandler(BaseHandler):

    def get(self,page=None):
        rows=self.cur.execute('select * from passage order by id desc')
        entry=self.cur.fetchall()

        if rows==0:
            pages=1
        elif rows%3==0:
            pages=rows/3
        else:
            pages=rows/3+1
        if page: 
            if int(page)<=0 or int(page)>pages:
                self.render('404.html')
            else:
                start=(int(page)-1)*3
                
                passage=entry[start:start+3]



                self.render('index.html',passage=passage,page=int(page),pages=pages)
        else:
            
            passage=entry[0:3]
            self.render('index.html',passage=passage,page=1,pages=pages)
        

    

class BlogHandler(BaseHandler):
    def get(self):
        islogin=self.is_login()
        

        if not islogin:
            self.redirect('/login')
        else:
            try:
                self.cur.execute("select name from cat")
                cat_names=self.cur.fetchall()
                self.render('back.html',cat_names=cat_names)
            except:
                self.render('404.html')
    def post(self):
        p_date=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        title=self.get_argument('title')
        author=self.get_argument('author')
        content=self.get_argument('context')
        url=self.get_argument('url')
        cat=self.get_argument('post_cat')
       
        try:
            self.cur.execute("select * from cat where name=%s",cat)
            cat_url=self.cur.fetchone()
            cat_id=cat_url['id']
            cat_slug=cat_url['slug']

        except:
            self.render('404.html')

        try:
            self.cur.execute("insert into passage(title,author,p_date,content,cat,url,cat_url)values(%s,%s,%s,%s,%s,%s,%s)",(title,author,p_date,content,cat,url,cat_slug))
            
            self.cur.execute("insert into cat_rel(post_id,cat_id) values((select max(id) from passage),%s)",cat_id)
            self.redirect('/')
        except:
            self.render('404.html')

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')
    def post(self):
        username=self.get_argument('username')
        passwd=self.get_argument('passwd')

        login=self.cur.execute("select * from user where username=%s and passwd=%s",(username,passwd))
        
        print login

        if login!=0:
            self.set_secure_cookie('cookie_name',username+passwd)
            self.write('yes')
        else:
            self.write('fuck')


class SingleHandler(BaseHandler):
    def get(self,name=None):
        if name:
            self.cur.execute("select * from passage where url=%s",name)
            row=self.cur.fetchone()
            self.render('page.html',row=row)
        else:
            self.render('404.html')

class CatHandler(BaseHandler):
    def get(self,cat_en_name=None):
        if cat_en_name:
            self.cur.execute("select * from passage where cat_url=%s order by id desc",cat_en_name)
            passage=self.cur.fetchall()
            cat=passage[0]['cat']

            self.render('cat.html',passage=passage,cat=cat)
        else:
            self.render('404.html')

class QuitHandler(BaseHandler):

    def get(self):
        self.set_secure_cookie('cookie_name','')
        self.redirect('/login')

class EditCatHandler(BaseHandler):
    def get(self):
        islogin=self.is_login()
        if not islogin:
            self.redirect('/login')
        else:
            try:
                self.cur.execute('select * from cat')
                cats=self.cur.fetchall()

                for cat in cats:
                   
                    num=self.cur.execute("select * from cat_rel where cat_id=%s",cat['id'])
                    
                    cat['num']=num
                self.render('edit-cat.html',cats=cats)
            except:
                self.render('404.html')

    def post(self):
        cat_name=self.get_argument('cat-name')
        cat_url=self.get_argument('cat-url')
        if cat_name and cat_url:
            try:
                self.cur.execute("insert into cat(name,slug)values(%s,%s)",(cat_name,cat_url.replace(' ','-')))
                self.redirect('/edit-cat')
            except:
                self.render('404.html')





class NavModule(tornado.web.UIModule):
    def render(self,pages,page):
        return self.render_string('modules/nav.html',pages=pages,page=page)

class EntryModule(tornado.web.UIModule):
    def render(self,passage):
        return self.render_string('modules/entry.html',passage=passage)

class HeaderNavModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('modules/header-nav.html')

class SidebarModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('modules/sidebar.html')

def main():
    parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__=='__main__':
	main()