"""Module to render evidently preset reports."""

from flask import Flask, render_template


app = Flask(__name__, template_folder="reports")


@app.route("/data-quality/amzn")
def data_quality_report_amzn():
    """
    Returns evidently preset reports as html
    """

    return render_template("preset_report_amzn.html")


@app.route("/data-quality/goog")
def data_quality_report_goog():
    """
    Returns evidently preset reports as html
    """

    return render_template("preset_report_goog.html")


@app.route("/data-quality/msft")
def data_quality_report_msft():
    """
    Returns evidently preset reports as html
    """

    return render_template("preset_report_msft.html")



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3600)
