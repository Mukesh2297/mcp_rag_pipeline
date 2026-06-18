from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import Document
from services import process_data, already_seeded


# def seed(db: Session):
#     if already_seeded(db):
#         print("Documents already seeded to db")
#         return
    
#     print("Seeding started")
#     unique_contexts = process_data()
#     total_context_count = len(unique_contexts)
#     print(f"Total context count : {total_context_count}")
#     with ThreadPoolExecutor(max_workers=20) as executor:
#         futures_to_be_completed = {
#             executor.submit(encode_one, context): (idx, context)
#             for idx, context in enumerate(unique_contexts)
#         }
#         for future in as_completed(futures_to_be_completed):
#             idx, context = futures_to_be_completed[future]
#             embedding = future.result()
#             new_document = Document(content=context, embedding=embedding)
#             db.add(new_document)
#             if idx % 100 == 0:
#                 print(f"{idx} Records processed ") 
#     db.commit()

#     print(f"Seeded {total_context_count} documents")


    
    



