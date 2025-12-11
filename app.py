import os
import io
import base64
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from utils.steg import embed_text_lsb, extract_text_lsb, analyze_text, embed_text_lsb_image, extract_text_lsb_image
from utils.watermark import add_text_watermark, add_image_watermark, add_text_watermark_image, add_image_watermark_image
from PIL import Image

app = Flask(__name__)
app.secret_key = "dev-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_IMAGES = {"png", "jpg", "jpeg", "bmp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGES


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/outputs/<path:filename>")
def outputs(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


@app.route("/watermark", methods=["GET", "POST"])
def watermark():
    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            flash("Pilih gambar terlebih dahulu")
            return redirect(url_for("watermark"))
        if not allowed_file(file.filename):
            flash("Format gambar tidak didukung")
            return redirect(url_for("watermark"))
        try:
            src_img = Image.open(file.stream)
        except Exception:
            flash("Gagal membaca gambar")
            return redirect(url_for("watermark"))

        mode = request.form.get("mode", "text")
        position = request.form.get("position", "bottom_right")
        margin = int(request.form.get("margin", 16))
        opacity = float(request.form.get("opacity", 0.6))
        if mode == "text":
            text = request.form.get("text", "")
            font_size = int(request.form.get("font_size", 32))
            color = request.form.get("color", "#ffffff")
            out_img = add_text_watermark_image(src_img, text, position=position, font_size=font_size, color=color, opacity=opacity, margin=margin)
        else:
            wm_file = request.files.get("wm_image")
            if not wm_file or wm_file.filename == "":
                flash("Pilih gambar watermark")
                return redirect(url_for("watermark"))
            try:
                wm_img = Image.open(wm_file.stream)
            except Exception:
                flash("Gagal membaca gambar watermark")
                return redirect(url_for("watermark"))
            scale = float(request.form.get("scale", 0.25))
            out_img = add_image_watermark_image(src_img, wm_img, position=position, scale=scale, opacity=opacity, margin=margin)

        buf = io.BytesIO()
        out_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        data_url = "data:image/png;base64," + b64
        return render_template("watermark.html", result=data_url)

    return render_template("watermark.html")


@app.route("/steg", methods=["GET", "POST"])
def steg():
    action = request.args.get("action") or request.form.get("action") or "embed"
    if request.method == "POST":
        if action == "embed":
            file = request.files.get("image")
            message = request.form.get("message", "")
            if not file or file.filename == "":
                flash("Pilih gambar terlebih dahulu")
                return redirect(url_for("steg", action="embed"))
            if not allowed_file(file.filename):
                flash("Format gambar tidak didukung")
                return redirect(url_for("steg", action="embed"))
            try:
                src_img = Image.open(file.stream)
                out_img = embed_text_lsb_image(src_img, message)
            except Exception as e:
                flash(str(e))
                return redirect(url_for("steg", action="embed"))
            buf = io.BytesIO()
            out_img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            data_url = "data:image/png;base64," + b64
            return render_template("steg.html", action="embed", result=data_url, success=True)
        else:
            file = request.files.get("image")
            if not file or file.filename == "":
                flash("Pilih gambar terlebih dahulu")
                return redirect(url_for("steg", action="extract"))
            if not allowed_file(file.filename):
                flash("Format gambar tidak didukung")
                return redirect(url_for("steg", action="extract"))
            try:
                src_img = Image.open(file.stream)
                text = extract_text_lsb_image(src_img)
            except Exception as e:
                flash(str(e))
                return redirect(url_for("steg", action="extract"))
            info = analyze_text(text)
            return render_template("steg.html", action="extract", extracted=text, success=True, rows=info["rows"], hex_view=info["hex_view"], raw_view=info["raw_view"], char_len=info["char_len"], byte_len=info["byte_len"]) 
    return render_template("steg.html", action=action)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

