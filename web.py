import logging

from flask import Flask, render_template, request
from datetime import datetime, timedelta

import processing

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error = None

    if request.method == "POST":
        try:

            n_time = request.form.get("n_time")

            selected_time = datetime.strptime(n_time, "%Y-%m-%dT%H:%M")

            min_time = datetime.now() + timedelta(minutes=1)

            if selected_time < min_time:
                error = "Wrong date or time or both."
                return render_template("index.html", data=None, error=error)

            data = {
                "client_name": request.form.get("client_name"),
                "n_method": request.form.get("n_method"),
                "n_text": request.form.get("n_text"),
                "n_time": request.form.get("n_time"),
                "priority": int(request.form.get("priority", 1)),
                "is_repeat": request.form.get("is_repeat") == "true"
            }
            # Send data to QID
            processing.send_to_qid(data)

            logging.info("Message sent to QID: %s", data)
        except Exception as exp:
            print(f"RabbitMQ error: {exp}")

    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
