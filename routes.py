from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from flask_migrate import Migrate
from flask_uploads import IMAGES
from flask_uploads import UploadSet