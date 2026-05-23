import psycopg

conn = psycopg.connect('postgresql://crm_user:crm_password@localhost:5432/crm_db')
cur = conn.cursor()

cur.execute("UPDATE applications SET status = 'REJECTED' WHERE status = 'Rejected';")
cur.execute("UPDATE applications SET status = 'INTERVIEW' WHERE status = 'Interview';")
cur.execute("UPDATE applications SET status = 'TECHNICAL_TEST' WHERE status = 'Technical Test';")
cur.execute("UPDATE applications SET status = 'FOLLOW_UP' WHERE status = 'Follow-up';")
cur.execute("UPDATE applications SET status = 'APPLIED' WHERE status = 'Applied';")
cur.execute("UPDATE applications SET status = 'WISHLIST' WHERE status = 'Wishlist';")

cur.execute("UPDATE applications SET type = 'ALTERNANCE' WHERE type = 'Alternance';")
cur.execute("UPDATE applications SET type = 'STAGE' WHERE type = 'Stage';")

conn.commit()
conn.close()
print("DB fixed")
