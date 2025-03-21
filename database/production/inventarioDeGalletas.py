from flask import render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

from db import app,mysql  

load_dotenv()

@app.route("/getInveGalletas")
def get_InveGalletas():
    return render_template("/production/InveGalletas.html")