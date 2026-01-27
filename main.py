# main.py
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from database import engine
from models import User, Activity, Challenge, Collection

app = FastAPI()
admin = Admin(app, engine)

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email, User.total_elevation]
    searchable_columns = [User.name, User.email]
    column_filters = ["country"]

class ActivityAdmin(ModelView, model=Activity):
    column_list = [Activity.id, Activity.climb_name, Activity.elevation]

class ChallengeAdmin(ModelView, model=Challenge):
    column_list = [Challenge.id, Challenge.title, Challenge.elevation, Challenge.start_date, Challenge.end_date]
    searchable_columns = [Challenge.title]

class CollectionAdmin(ModelView, model=Collection):
    column_list = [Collection.id, Collection.title]
    searchable_columns = [Collection.title]

admin.add_view(UserAdmin)
admin.add_view(ActivityAdmin)