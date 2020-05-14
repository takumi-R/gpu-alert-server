from flask import Flask,request,abort,jsonify
import numpy as np
import os
from slackclient import SlackClient
app = Flask(__name__)
verfica_token = os.environ.get("VERFICA_TOKEN")
slack_token = os.environ.get("SLACK_API_TOKEN")
gpu_dict = dict()
gpu_dict_users =[] 

def add_alarm(channel_id,gpu_id = None,gpu_mem = 1000):
    gpu_dict_users.append({ "channel_id":channel_id,'gpu_id':gpu_id,'mem' : np.array(gpu_mem) })
def send_alarm(channel_id,gpu_id = None):
        print("sending")
        ls_str = "gpu_id:" + str(gpu_id) + " has enough memory for you"
        sc = SlackClient(slack_token)
        M=sc.api_call(
            "chat.postMessage",
             channel=channel_id,
             text=ls_str
                  )

@app.route('/gpu_status',methods=["POST"])
def hello():
    if not request.json :
          abort(400)
    content = request.json
    print(content)
    if not 'gpu_id' in content:
          abort(400)
    if not 'gpu_size' in content:
          abort(400)
    if not 'gpu_mem' in content:
          abort(400)
    gpu_dict[content['gpu_id']] = { 'size' :content['gpu_size'] , 'mem' : content['gpu_mem'],'name' : content['name'] }
    for gpu_dict_int in range(len(gpu_dict_users)):
        if int((np.array(gpu_dict[gpu_dict_users[gpu_dict_int]['gpu_id']]['size']) - gpu_dict_users[gpu_dict_int]['mem']).max())<0:
            send_alarm(gpu_dict_users[gpu_dict_int]['channel_id'],gpu_dict_users[gpu_dict_int]['gpu_id'])
            del gpu_dict_users[gpu_dict_int]
    return "200"
@app.route('/slack_gpu',methods=["POST"])
def slack_gpu():
    if request.form['token'] == str(verfica_token):
        relay_str = "/remind_gpu " + request.form['text'] + "\n"
    else:
        abort(400)
    if request.form['text'] == str("ls") :
        ls_str = ""
        for gpu_dict_key in gpu_dict.keys():
            ls_str += "gpu_id:" + str(gpu_dict_key) + "    hostname:" + str(gpu_dict[gpu_dict_key]['name'])
        return jsonify({'text':ls_str})
    if request.form['text'] == str("help") :
        ls_str="         User  Commands\nname\n      /remind_gpu -- set alert for gpu memory\nSYNOPSIS\n      /remind_gpu [OPTIONS]\n      /remind_gpu [gpu_id] [MEMORY_LIST]\nDESCRIPTION\n    Alerts user when gpu_ids memory usage get lower than MEMORY_LIST\n    ls\n        prints the correspondence between gpu_id:hostname\n    help\n        prints this message\nEXAMPLE\n    /remind_gpu 0 500,500\n        When gpu_id=0s first gpu memory usage gets lower than 500MiB and\n        second gpu memory usage gets lower than 500MiB the alert will be sent"
        return jsonify({'text':ls_str})
    elif len(request.form['text'].split(" ")) == 2:
        gpu_id,gpu_mem= request.form['text'].split(" ")
        try:
            gpu_id = int(gpu_id)
            gpu_mem = map(int,gpu_mem.split(","))
            gpu_mem = list(gpu_mem)
        except:
            return jsonify({'text':relay_str + "unknown format"})
        add_alarm(request.form['channel_id'],gpu_id,gpu_mem)
        return jsonify({'text':relay_str+"alert has been set"})
    else:
        ls_str="         User  Commands\nname\n      /remind_gpu -- set alert for gpu memory\nSYNOPSIS\n      /remind_gpu [OPTIONS]\n      /remind_gpu [gpu_id] [MEMORY_LIST]\nDESCRIPTION\n    Alerts user when gpu_ids memory usage get lower than MEMORY_LIST\n    ls\n        prints the correspondence between gpu_id:hostname\n    help\n        prints this message\nEXAMPLE\n    /remind_gpu 0 500,500\n        When gpu_id=0s first gpu memory usage gets lower than 500MiB and\n        second gpu memory usage gets lower than 500MiB the alert will be sent"
        return jsonify({'text':ls_str})
if __name__ == '__main__':
        app.run(host='0.0.0.0',ssl_context='adhoc',port=8081)




