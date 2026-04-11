from backend.database import SessionLocal, UserEvaluation
db = SessionLocal()
for ev in db.query(UserEvaluation).all():
    print(ev.user_id, repr(ev.long_term_evaluation))
