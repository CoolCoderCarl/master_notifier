import logging

from flask import Flask, render_template, request

import processing

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    data = None

    if request.method == "POST":
        try:
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

            logging.info("Message sent to QID: ", data)
        except Exception as exp:
            print(f"RabbitMQ error: {exp}")

    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
