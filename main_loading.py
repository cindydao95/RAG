from source_code.pipeline.loading_pipeline import Load
import os

def load_env_vars():
    from dotenv import load_dotenv
    load_dotenv()
    db_name = os.getenv("DB_NAME")
    host = os.getenv("HOST")
    password = os.getenv("PASSWORD")
    port = os.getenv("PORT")
    user = os.getenv("USER")
    return db_name,host,password,port,user

if __name__ == "__main__":
    table_name = "imm_law"

    f_names =["post_06_14_24.txt"]
    db_name,host,password,port,user =load_env_vars()
    pipeline = Load(f_names=f_names)
    pipeline.start_load_docs()
    pipeline.start_embedding()
    pipeline.start_storage(host=host,password=password,port=port,
                        user=user,db_name=db_name,table_name=table_name)



