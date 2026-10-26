"""team.py - who built BBV ISS LIVE.  Edit names, roles and photos here.

Photos live in assets/team/.  If you prefer not to publish photos, set
SHOW_PHOTOS = False (initials are shown instead) or delete the picture files.
"""

SHOW_PHOTOS = True

# Role keys refer to texts in i18n.py (role_<key>_t = title, role_<key>_d = description).
STUDENTS = [
    {"name": "Ms. Omanshi Dubey", "photo": "omanshi_dubey.jpg",
     "roles": ["data", "app", "present"]},
    {"name": "Ms. Radha Gupta", "photo": "radha_gupta.jpg",
     "roles": ["viz", "deploy", "present"]},
]

MENTORS = [
    {"name": "Mrs. Ruchi", "post": "HOD (CS)", "photo": "Ruchi.jpg"},
    {"name": "Mr. Shobhit Daga", "post": "PGT (CS)", "photo": "shobhit_daga.jpg"},
    {"name": "Mrs. Nishi Soni", "post": "TGT (CS)", "photo": "nishi_soni.jpg"},
]
