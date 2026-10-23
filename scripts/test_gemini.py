from app.services.gemini_service import generate_sql


question = "Which 5 merchants generated the highest revenue?"


sql = generate_sql(question)


print("\nGenerated SQL:")
print(sql)
