from backend.database import SessionLocal, User, DbItinerary, UserEvaluation
import os

db = SessionLocal()
users = db.query(User).all()
print("Users:", [u.username for u in users])

itineraries = db.query(DbItinerary).all()
print("Itineraries count:", len(itineraries))

evaluations = db.query(UserEvaluation).all()
print("Evaluations count:", len(evaluations))

