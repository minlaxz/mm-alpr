import cv2,os,pickle
data_images = []
labels = []
input_path = 'dataset'
for _, dirs, files in os.walk(input_path):
    for dir in dirs:
        print(" Dir_Name :\t " + dir)
        for filename in os.listdir(input_path + "/" + dir):
            if filename.endswith('.jpg'):
                gray = cv2.cvtColor(cv2.imread(input_path + "/" + dir + "/" + filename), cv2.COLOR_BGR2GRAY)
                data_images.append(gray)
                labels.append(dir)
pickle.dump(data_images, open("data.pickle", "wb"))
pickle.dump(labels, open("labels.pickle", "wb"))
print('Length data : ' + str(len(data_images)))
print('Length labels : ' + str(len(labels)))
print('Processs finished !')
