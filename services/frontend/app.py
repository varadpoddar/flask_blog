import os
from urllib.parse import urljoin

import requests
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

BLOG_API_BASE = os.getenv("BLOG_API_BASE", "http://localhost:5001/")
AUTH_API_BASE = os.getenv("AUTH_API_BASE", "http://localhost:5002/")  # reserved for future use

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")


def api_url(base, path):
    return urljoin(base, path.lstrip("/"))


def get_post(post_id):
    resp = requests.get(api_url(BLOG_API_BASE, f"/posts/{post_id}"), timeout=5)
    if resp.status_code == 404:
        abort(404)
    resp.raise_for_status()
    return resp.json()


@app.route("/")
def index():
    resp = requests.get(api_url(BLOG_API_BASE, "/posts"), timeout=5)
    resp.raise_for_status()
    posts = resp.json()
    return render_template("index.html", posts=posts)


@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    return render_template("post.html", post=post)


@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title:
            flash("Title is required!")
        else:
            resp = requests.post(
                api_url(BLOG_API_BASE, "/posts"),
                json={"title": title, "content": content},
                timeout=5,
            )
            if resp.status_code == 201:
                return redirect(url_for("index"))
            msg = resp.json().get("error") if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            flash(f"Error creating post: {msg}")
    return render_template("create.html")


@app.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id):
    post = get_post(id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title:
            flash("Title is required!")
        else:
            resp = requests.put(
                api_url(BLOG_API_BASE, f"/posts/{id}"),
                json={"title": title, "content": content},
                timeout=5,
            )
            if resp.status_code == 200:
                return redirect(url_for("index"))
            msg = resp.json().get("error") if resp.headers.get("content-type", "").startswith("application/json") else resp.text
            flash(f"Error updating post: {msg}")
    return render_template("edit.html", post=post)


@app.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    post = get_post(id)
    resp = requests.delete(api_url(BLOG_API_BASE, f"/posts/{id}"), timeout=5)
    if resp.status_code not in (200, 204):
        msg = resp.json().get("error") if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        flash(f"Error deleting post: {msg}")
        return redirect(url_for("index"))
    flash(f'"{post["title"]}" was successfully deleted!')
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
