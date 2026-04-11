from backend.database import SessionLocal, UserEvaluation

db = SessionLocal()
evals = db.query(UserEvaluation).all()
for ev in evals:
    if ev.recent_evaluation:
        ev.recent_evaluation = ev.recent_evaluation.replace('**', '').replace('###', '').strip()
    if ev.long_term_evaluation:
        ev.long_term_evaluation = ev.long_term_evaluation.replace('**', '').replace('###', '').strip()
db.commit()
print("Cleaned up existing evaluations")
