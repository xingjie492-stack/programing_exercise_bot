from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Submissions
from flask_login import login_required, current_user
import os
from dotenv import load_dotenv
import google.generativeai as genai
from forms import UsersAnswer
from datetime import datetime