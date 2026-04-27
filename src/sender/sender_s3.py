# %%
import datetime
import os
import pandas as pd


# %%

class S3Sender:

    def __init__(self, s3_client):
        self.s3_client = s3_client
        self.data_path_prefix = "../data/"

    def upload_folder(self, foldername, batch_size=1000):
        
        folder = os.path.join(self.data_path_prefix, foldername)
        files = [i for i in os.listdir(folder) if i.endswith(".parquet")]

        while len(files) > 0:
            
            files_process = files[:batch_size]
            
            dfs = [pd.read_parquet(os.path.join(folder, i)) for i in files_process]
            df = pd.concat(dfs)

            local_filename = f"batch_{foldername}.parquet"
            df.to_parquet(local_filename)

            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
            
            self.s3_client.upload_file(
                local_filename,
                "datalake-raw-tmw",
                f"dota2/{foldername}/{now}.parquet",
            )

            os.remove(local_filename)

            for i in files_process:
                files.remove(i)
                os.remove(os.path.join(folder, i))


    def upload_all(self, batch_size=1000):
        self.upload_folder("match_details", batch_size=batch_size)
        self.upload_folder("match_player_details", batch_size=batch_size)
        self.upload_folder("leagues", batch_size=batch_size)


