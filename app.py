from flask import Flask, render_template, request, json, jsonify, session
import warnings, time
from flask.helpers import url_for
warnings.filterwarnings("ignore")
from werkzeug.utils import secure_filename
import os
import csv
import uuid

app = Flask(__name__, static_url_path='/static')
app.secret_key = "abc123"
org_audio_dir = "preprocess_eval_audio"
diffwave_audio_dir = "preprocess_syn_audio"
pretrained_melgan_dir = "preprocess_syn_audio_pretrained_MelGAN"
retrained_melgan_dir = "preprocess_syn_audio_retrained_MelGAN"
mos_pretrained_melgan = "mos/pretrained_melgan"
mos_retrained_melgan = "mos/retrained_melgan"
mos_diffwave = "mos/diffwave"

@app.route("/<model>", methods=['GET','POST'])
def main(model):
    session_id = uuid.uuid4()
    session['id'] = session_id
    f = open("survey_audio.txt", "r")
    list_audio = f.readlines()
    list_audio = [audio_fp.strip("\n") for audio_fp in list_audio]
    list_audio = list_audio[:2]
    id = [i for i in range(2)]
    if model == "diffwave":
        syn_audio_dir = diffwave_audio_dir
        mos_dir = mos_diffwave
    elif model == "retrained_melgan":
        syn_audio_dir = retrained_melgan_dir
        mos_dir = mos_retrained_melgan
    else:
        syn_audio_dir = pretrained_melgan_dir
        mos_dir = mos_pretrained_melgan

    ref_fp = [os.path.join(org_audio_dir, audio_fp) for audio_fp in list_audio]
    syn_fp = [os.path.join(syn_audio_dir, audio_fp) for audio_fp in list_audio]
    items = zip(id, ref_fp, syn_fp)
    return render_template('rendered_mos.html', items=items, model=model, session_id=session_id)

@app.route("/submit", methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        name = str(session['id'])
        gender = request.form['gender']
        age = request.form['age']
        model = request.form['model']
        data = request.form
        values = list(data.listvalues())[3:-2]
        list_mos = [int(mos[0]) for mos in values]
        audio_id = [i for i in range(len(list_mos))]
        if model == "diffwave":
            mos_dir = mos_diffwave
        elif model == "retrained_melgan":
            mos_dir = mos_retrained_melgan
        else:
            mos_dir = pretrained_melgan_dir

        ####### write mos into csv files #######################################################
        f = open(os.path.join('static', mos_dir, name+"_"+age+"_"+gender+".csv"), "w")
        writer = csv.writer(f)
        writer.writerow(["Audio id", "MOS"])

        for id, mos in zip(audio_id, list_mos):
            writer.writerow([id, mos])
        ########################################################################################


        print(data)
        print(list_mos)
        return render_template('thankyou.html', model=model)
    return render_template('rendered_mos.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5016)