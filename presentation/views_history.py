from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Submissions
from flask_login import login_required, current_user
from forms import UsersAnswer
from datetime import datetime
from presentation.views import generate_content