#coding: utf-8
import os
import datetime
import random
import json
import re
from pymongo import MongoClient
from flask import Flask,request,url_for
from flask import render_template,make_response

app = Flask(__name__)

client = MongoClient("127.0.0.1",27017)
db = client["edu"]
col = db["res"]

@app.route("/")
def test():
    return render_template("ck.html")

def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@app.route('/ckupload/', methods=['POST'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.static_folder, 'upload', rnd_name)
        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """
            <script type="text/javascript">
            window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
            </script>
        """ % (callback, url, error)
    res2 = {
        "fileName": rnd_name,
        "uploaded": 1,
        "url": url
    }
    if callback != '1':
        response = make_response(json.dumps(res2))
    else:
        response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

@app.route('/upload/', methods=['POST'])
def upload():
    """CKEditor file upload"""
    error = ''
    url = ''
    if request.method == 'POST':
        ret = request.json
        col.insert({"data":ret})
    return 'success save',200

@app.route('/gettm/', methods=['GET'])
def hqtm():
    """CKEditor file upload"""
    error = ''
    url = ''
    data = col.find_one({},{"_id":0})
    return data.get("data")["data"],200

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=8000)