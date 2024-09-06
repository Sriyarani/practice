from http.server import BaseHTTPRequestHandler, HTTPServer
import mariadb
import cgi
from jinja2 import Environment, FileSystemLoader
#import os
# import urllib.parse.parse_qsl
# import email.message
class RequestHandler(BaseHTTPRequestHandler):


    def do_GET(self):

        self.routes = {
            "/": self.home,
            "/submit": self.process,
        }

        handler = self.routes.get(self.path, self.handle_not_found)
        handler()

    def do_POST(self):
        self.routes = {
            "/": self.home,
            "/submit": self.process,
        }


        handler = self.routes.get(self.path, self.handle_not_found)
        handler()


    def home(self):
        self.env = Environment(loader=FileSystemLoader('.'))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        template = self.env.get_template('/index.html')
        self.wfile.write(bytes(template.render(message='hello'), 'utf-8'))
        # fh = open('index.html', 'rb')
        # string = fh.read()
        # self.wfile.write(string)

    def process(self):

        # Parse the form data
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     }
        )

        # Get the form values
        first_name = form.getvalue("name")
        age = form.getvalue("age")

        conn = mariadb.connect(
            user="root",
            password="root",
            host="localhost",
            port=3306,
            database="test"
        )
        cur = conn.cursor()

        # query = "INSERT INTO student(name,age)"
        sql = "INSERT INTO student(name,age) VALUES (%s, %s)"
        val = (first_name, age)
        cur.execute(sql, val)
        conn.commit()

        # cur.execute(query)


        student_res = []
        cur.execute("SELECT * FROM student")
        # Fetch the results
        for row in cur.fetchall():
            student_res.append(row)

        msg = "My name is {} and age is {}".format(first_name,str(age))

        self.env = Environment(loader=FileSystemLoader('.'))
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        template = self.env.get_template('/index.html')
        self.wfile.write(bytes(template.render(message=student_res), 'utf-8'))

        # self.wfile.write(b"<h1>About Us</h1>")

    def handle_not_found(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(b"<h1>Page not found</h1>")

if __name__ == "__main__":
    server_address = ("", 81)
    httpd = HTTPServer(server_address, RequestHandler)
    print("Server running on port 8000...")
    httpd.serve_forever()