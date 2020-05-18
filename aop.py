from flask import Flask,request,abort,jsonify
import numpy as np
import os
from slackclient import SlackClient
import database as D
app = Flask(__name__)
verfica_token = os.environ.get("VERFICA_TOKEN")
slack_token = os.environ.get("SLACK_API_TOKEN")
def send_alarm(channel_id,pc_id):
        print("sending")
        ls_str = "pc_id:" + str(pc_id) + " has enough memory for you"
        sc = SlackClient(slack_token)
        M=sc.api_call(
            "chat.postMessage",
             channel=channel_id,
             text=ls_str
                  )
        print(M)

@app.route('/gpu_status',methods=["POST"])
def hello():
    gpu_database = D.database_set()
    if not request.json :
          abort(400)
    content = request.json
    if not 'gpu_id' in content:
          abort(400)
    if not 'gpu_size' in content:
          abort(400)
    if not 'gpu_mem' in content:
          abort(400)
    gpu_database.set_gpu(content)      
    channel_id_list =  gpu_database.check_reserv()   
    for channel_id in channel_id_list:
        send_alarm(channel_id[0],channel_id[1])
    del gpu_database
    return "200"
@app.route('/slack_gpu',methods=["POST"])
def slack_gpu():
    gpu_database = D.database_set()
    if request.form['token'] == str(verfica_token):
        relay_str = "/remind_gpu " + request.form['text'] + "\n"
    else:
        abort(400)
    if request.form['text'] == str("ls") :
        ls_str = ""
        for ls_name_item in gpu_database.ls_name():
             ls_str += "pc_id:" + str(ls_name_item[0]) + "    hostname:" + str(ls_name_item[1])
        del gpu_database
        return jsonify({'text':ls_str})
    elif len(request.form['text'].split(" ")) == 2:
        gpu_id,gpu_mem= request.form['text'].split(" ")
        try:
            gpu_id = int(gpu_id)
            gpu_mem = map(int,gpu_mem.split(","))
            gpu_mem = list(gpu_mem)
        except:
            del gpu_database
            return jsonify({'text':relay_str + "failed to set alert"})
        else:
            print(gpu_database.get_gpu_num(gpu_id))
            print(len(gpu_mem))
            if gpu_database.get_gpu_num(gpu_id) < len(gpu_mem):
                return jsonify({'text':relay_str + "too many gpus"})
            else: 
                print("aho")   
                gpu_database.set_reserv(request.form['channel_id'],gpu_id,gpu_mem)      
        del gpu_database
        return jsonify({'text':relay_str+"alert has been set"})
    else:
        ls_str="         User  Commands\nname\n      /remind_gpu -- set alert for gpu memory\nSYNOPSIS\n      /remind_gpu [OPTIONS]\n      /remind_gpu [pc_id] [MEMORY_LIST]\nDESCRIPTION\n    Alerts user when pc_ids memory usage get lower than MEMORY_LIST\n    ls\n        prints the correspondence between pc_id:hostname\n    help\n        prints this message\nEXAMPLE\n    /remind_gpu 0 500,500\n        When pc_id=0s first gpu memory usage gets lower than 500MiB and\n        second gpu memory usage gets lower than 500MiB the alert will be sent"
        return jsonify({'text':ls_str})
if __name__ == '__main__':
        app.run(host='0.0.0.0',ssl_context='adhoc',port=8081)




