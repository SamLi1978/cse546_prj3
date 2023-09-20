from boto3 import client as boto3_client
import face_recognition
import pickle
from numpy import ndarray
import os

input_bucket = "cse546-p3-in-s3"
output_bucket = "cse546-p3-out-s3"
video_path = "video_downloaded"
frame_path = "frame_extracted"

def download_videos_from_in_s3(in_s3):
    s3 = boto3_client('s3')
    list_obj = s3.list_objects_v2(Bucket=in_s3)
    try:
        for item in list_obj["Contents"]:
            file_name = item["Key"]
            print(file_name)
        
            if not os.path.exists(video_path): 
                os.makedirs(video_path)

            with open(f'{video_path}/{file_name}', "wb") as f:
                s3.download_fileobj(in_s3, file_name, f)
    except Exception as e:
        print(e)

#ffmpeg -i test_0.mp4 -frames:v 1 a.jpeg

def extract_image_from_video():
    for filename in os.listdir(video_path):
        if filename.endswith(".mp4") or filename.endswith(".MP4"):
            print(filename)
            filetitle = filename.rsplit('.')
            print(filetitle[0])
            if not os.path.exists(frame_path): 
                os.makedirs(frame_path)
            os.system("ffmpeg -i " + f'{video_path}/{filename}' + " -frames:v 1 " + f"{frame_path}/{filetitle[0]}.jpeg")

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def face_recognition_handler(event, context):	
	print("Hello")


if __name__ == '':

    da = open_encoding('encoding')
    print(da['name'])
    #print(da['encoding'])
    nd = da['encoding'][-1]
    print(type(nd))
    print(nd)
    l = nd.tolist()
    #print(l)
    #print(len(l))

    known_image = face_recognition.load_image_file("test001.jpeg")
    #print(type(known_image))
    #print(known_image)
    encoding_a = face_recognition.face_encodings(known_image)[0]
    print(type(encoding_a))
    print(encoding_a)


    results = face_recognition.compare_faces(nd, [encoding_a])
    print(results)

if __name__ == '__main__':
    #download_videos_from_in_s3(input_bucket)
    extract_image_from_video()
