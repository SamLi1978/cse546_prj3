from boto3 import client as boto3_client
import os

input_bucket = "cse546-p3-in-s3"
output_bucket = "cse546-p3-out-s3"
test_cases = "test_cases/"

def clear_bucket(bucket):

    global input_bucket
    s3 = boto3_client('s3')
    list_obj = s3.list_objects_v2(Bucket=bucket)
    try:
        for item in list_obj["Contents"]:
            key = item["Key"]
            s3.delete_object(Bucket=bucket, Key=key)
            print(f'{key} removed from the bucket {bucket}')
    except Exception as e:
        print(e)

def upload_to_input_bucket_s3(path, name):

	global input_bucket
	s3 = boto3_client('s3')
	s3.upload_file(path + name, input_bucket, name)
	
	
def upload_files(test_case):	

	global input_bucket
	global output_bucket
	global test_cases
	
	# Directory of test case
	test_dir = test_cases + test_case + "/"
	
	# Iterate over each video
	# Upload to S3 input bucket
	for filename in os.listdir(test_dir):
		if filename.endswith(".mp4") or filename.endswith(".MP4"):
			upload_to_input_bucket_s3(test_dir, filename)
			print(f"{str(filename)} uploaded to the bucket {input_bucket}") 
			
	
def workload_generator():
	
	#print("Running Test Case 1")
	#upload_files("test_case_1")

	print("Running Test Case 2")
	upload_files("test_case_2")

if __name__ == '__main__':
	
    clear_bucket(input_bucket)
    clear_bucket(output_bucket)	
    workload_generator()	
	

