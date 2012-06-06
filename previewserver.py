import flask
import codecs
import markdown
import os
import json
app = flask.Flask(__name__)
import datetime
import re

EXTENSIONS = ["markdown", "md", "mkd", "txt"]

@app.before_request
def beforeRequest():
  app.jinja_env.globals["generated"] = datetime.datetime.now()

def getFilename(folder, name):
  for ext in EXTENSIONS:
    filename = "%s/%s.%s" % (folder, name, ext)
    if os.path.exists(filename):
      return filename

  filename = "%s/%s" % (folder, name)
  if os.path.exists(filename):
    return filename
  else:
    return None

sectionHeadersRegex = re.compile(r"(===)\W+(\w+)\W+(===)")
sectionBodyRegex = r"===\W+%s\W+===(.+)---\W+%s\W+---"
def retrieveContent(folder, name):
  filename = getFilename(folder, name)
  if filename is None:
    return None

  f = codecs.open(filename, mode="r", encoding="utf8")
  text = f.read()
  f.close()

  sectionHeaders = sectionHeadersRegex.findall(text)
  if len(sectionHeaders) == 0:
    return {"content" : markdown.markdown(text)}
  else:
    sections = {}
    for section in sectionHeaders:
      sectionName = section[1]
      sectionBody = re.findall(sectionBodyRegex % (sectionName, sectionName), text, flags=re.S)[0]
      sectionBody = sectionBody.strip()
      sections[sectionName] = markdown.markdown(sectionBody)
    return sections

def retrieveMeta(folder, name):
  f = codecs.open("%s/%s.meta" % (folder, name), mode="r", encoding="utf8")
  text = f.read()
  f.close()
  return json.loads(text)

@app.route("/blog/")
def displayBlog(): #TODO: not complete
  return flask.render_template("blog.html")

@app.route("/blog/<postname>/")
def displayPost(postname):
  content = retrieveContent("posts", postname)
  meta = retrieveMeta("posts", postname)
  if content is None:
    return flask.abort(404)
  return flask.render_template("post.html", post=postname,
      title=meta.pop("title"), meta=meta, **content)

@app.route("/<pagename>/")
def displayPage(pagename):
  if pagename == "favicon.ico":
    return flask.abort(404)# TODO: Implement this

  content = retrieveContent("pages", pagename)
  meta = retrieveMeta("pages", pagename)
  template = meta.get("template", "website.html")
  if content is None:
    return flask.abort(404)

  return flask.render_template(template, page=pagename,
      title=meta.pop("title"), meta=meta, **content)

@app.route("/")
def home():
  return flask.redirect(flask.url_for("displayPage", pagename="home"))

if __name__ == "__main__":
  app.run(debug=True, host="")