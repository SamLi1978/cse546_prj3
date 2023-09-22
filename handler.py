import boto3
import face_recognition
import pickle
from numpy import ndarray
import os
import csv

input_bucket = "cse546-p3-in-s3"
output_bucket = "cse546-p3-out-s3"
video_path = "video_downloaded"
frame_path = "frame_extracted"
student_info_path = "student_info"

def download_videos_from_in_s3(s3):
    
    mp4_file_list = []

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



def load_dynamodb():
    dynamodb = boto3.resource('dynamodb')
    student_table = dynamodb.Table('student')

    dataset = student_table.scan()
    items = dataset['Items']
    return items


def find_item(name, items):
    for item in items:
        if (name == item['name']):
            return item
    return None


def save_and_get_csv_file(filetitle, name, major, year):
    if not os.path.exists(student_info_path): 
        os.makedirs(student_info_path)    
    filename = f'{student_info_path}/{filetitle}.csv'
    #print(filename)
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile) 
        writer.writerow([name, major, year])

def upload_csv_file_to_s3(s3, filename):    
    file_name = f'{student_info_path}/{filename}'
    s3.upload_file(file_name, output_bucket, filename)


def face_recognition_handler(event, context):	
	print("Hello")


if __name__ == '__main__':

    s3 = boto3.client('s3')

    items = load_dynamodb()

    encodings = open_encoding('encoding')
    #print(encodings)

    mp4_list = download_videos_from_in_s3(s3)
    #print(mp4_list)
    
    for mp4_file in mp4_list:

        jpeg_file = extract_image_from_video(mp4_file)
        #print(jpeg_file)

        face_encoding = get_face_encoding(jpeg_file)   
        person = search_face_from_encodings(face_encoding, encodings)     
        if (person != None):
            item = find_item(person[0], items)
            if (item != None):
                print(mp4_file, item['name'], item['major'], item['year'])
                file_title_and_ext = mp4_file.rsplit('.')
                file_title = file_title_and_ext[0]
                save_and_get_csv_file(file_title, item['name'], item['major'], item['year'])
                upload_csv_file_to_s3(s3, f'{file_title}.csv')
