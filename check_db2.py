from backend.database import SessionLocal, DbItinerary, UserEvaluation

db = SessionLocal()
print("--- ITINERARIES ---")
for it in db.query(DbItinerary).filter(DbItinerary.is_saved == True).all():
    print(it.id, it.user_id, it.destination)

print("--- EVALUATIONS ---")
for ev in db.query(UserEvaluation).all():
    print(ev.user_id, repr(ev.recent_evaluation))

