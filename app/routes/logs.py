from flask_login import login_required, current_user
from flask import render_template, request, flash, json
from datetime import datetime, timedelta
from models import *
from config import *
from functions import *

@app.route('/logs', methods=['POST', 'GET'])
@login_required
def handle_logs():
    productResults = query_products()
    if request.method == 'POST':
        bmpid = int(request.form.get("bmpid"))
        lastqc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = current_user.name
        requirements = request.form.get("requirements")
        if not requirements:
            requirements = "{\"None\" : \"N/A\"}"
        requirements = json.loads(requirements)

        new_log = LogsModel(bmpid, lastqc, user, requirements)
        db.session.add(new_log)
        db.session.commit()
        results = query_logs()
        return render_template('logs.html', results=results, productResults=productResults, status_good=f"Success! Log: '{new_log.id}' has been created.")
    elif request.method == 'GET':
        results = query_logs()
        if len(results) == 0:
            return render_template('logs.html', productResults=productResults, no_logs="No Logs to Display")
        else:
            return render_template('logs.html', productResults=productResults, results=results)

@app.route('/logs/<log_id>', methods=['GET', 'POST', 'DELETE'])
def handle_log(log_id):
    log = LogsModel.query.get_or_404(log_id)
    response = {
            "id" : log.id,
            "bmpid": log.bmpid,
            "lastqc": log.lastqc,
            "user" : log.user,
            "requirements": log.requirements
        }
    if request.method == 'GET':
        return {"message": "success", "product": response}

    elif request.method == 'POST':
        # This will update the product in the product table.
        # If editing the BMP ID, then the QC table will need to be updated as well.
        flash("OK")
        return{"POST": "POST THINGY"}

    elif request.method == 'DELETE':
        logDate = LogsModel.query.filter_by(id=log_id).first()
        if (logDate.lastqc > (datetime.now() - timedelta(days=2))):
            db.session.delete(log)
            db.session.commit()
            flash("QC Log successfully deleted.")
            return {"Success": "QC Log has been deleted."}
        else:
            flash("QC Log unable to be deleted since it was entered over 24 hours ago.")
            return {"Success": "QC Log not deleted."}

