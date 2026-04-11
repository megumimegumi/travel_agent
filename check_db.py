from backend.database import SessionLocal, DbItinerary, UserEvaluation

db = SessionLocal()
print("--- ITINERARIES ---")
for it in db.query(DbItinerary).all():
    print(it.id, it.user_id, it.destination, it.created_at, it.is_saved)

print("--- EVALUATIONS ---")
for ev in db.query(UserEvaluation).all():
    print(ev.user_id, type(ev.recent_evaluation))

