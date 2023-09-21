from boto3 import client as boto3_client
import face_recognition
import pickle
from numpy import ndarray
import os

input_bucket = "cse546-p3-in-s3"
output_bucket = "cse546-p3-out-s3"
video_path = "video_downloaded"
frame_path = "frame_extracted"

def download_videos_from_in_s3():
    
    mp4_file_list = []
    
    s3 = boto3_client('s3')
    list_obj = s3.list_objects_v2(Bucket=input_bucket)

    try:
        for item in list_obj["Contents"]:
            file_name = item["Key"]
            print(file_name)
            mp4_file_list.append(file_name)
        
            if not os.path.exists(video_path): 
                os.makedirs(video_path)

            with open(f'{video_path}/{file_name}', "wb") as f:
                s3.download_fileobj(input_bucket, file_name, f)

        return mp4_file_list

    except Exception as e:
        print(e)

'''
ffmpeg -y -i test_0.mp4 -frames:v 1 a.jpeg > /dev/null 2>&1
'''

def extract_image_from_video(mp4_file):

    filetitle = mp4_file.rsplit('.')
    
    #print(filetitle[0])
    if not os.path.exists(frame_path): 
        os.makedirs(frame_path)
    os.system("ffmpeg -y -i " + f'{video_path}/{mp4_file}' + " -frames:v 1 " + f"{frame_path}/{filetitle[0]}.jpeg > /dev/null 2>&1")

    return f"{filetitle[0]}.jpeg"
        

def search_face_from_encodings(face_encoding, encodings):

    name_list = encodings['name']
    encoding_list = encodings['encoding']

    for i in range(0, len(name_list)):
        name = name_list[i]
        #print(name)
        encoding = encoding_list[i]
        #print(encoding)
        #print(face_encoding)
        result = face_recognition.compare_faces([face_encoding], encoding)
        if (result[0] == True):
            return (name,encoding)
    
    return None

def get_face_encoding(jpeg_file):
    
    image_data = face_recognition.load_image_file(f"{frame_path}/{jpeg_file}")
    face_encoding = face_recognition.face_encodings(image_data)[0]
    #print(face_encoding)
    return face_encoding
            

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def face_recognition_handler(event, context):	
	print("Hello")


if __name__ == '__main__':

    encodings = open_encoding('encoding')
    #print(encodings)

    mp4_list = download_videos_from_in_s3()
    #print(mp4_list)
    
    for mp4_file in mp4_list:

        jpeg_file = extract_image_from_video(mp4_file)
        #print(jpeg_file)

        face_encoding = get_face_encoding(jpeg_file)   
        person = search_face_from_encodings(face_encoding, encodings)     
        if (person != None):
            print(mp4_file, person[0])
    
