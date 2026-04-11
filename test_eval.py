from backend.database import SessionLocal, DbItinerary, UserEvaluation
from backend.main import update_user_evaluation_in_bg

db = SessionLocal()
item = DbItinerary(user_id='test1234', destination='Paris', is_saved=True)
db.add(item)
db.commit()

try:
    update_user_evaluation_in_bg('test1234')
except Exception as e:
    print("FAILED", e)

ue = db.query(UserEvaluation).filter_by(user_id='test1234').first()
if ue:
    print("Recent: ", ue.recent_evaluation)
else:
    print("User Evaluation Empty")

