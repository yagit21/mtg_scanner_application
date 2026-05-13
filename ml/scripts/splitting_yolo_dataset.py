import os
import shutil

#Paths
src = "ml/data/augmented"
base_out = "ml/data/yolo_dataset"

train_img = os.path.join(base_out, "images/train")
val_img = os.path.join(base_out, "images/val")

train_lbl = os.path.join(base_out, "labels/train")
val_lbl = os.path.join(base_out, "labels/val")

#Creating the paths/making sure they exist
os.makedirs(train_img, exist_ok=True)
os.makedirs(val_img, exist_ok=True)
os.makedirs(train_lbl, exist_ok=True)
os.makedirs(val_lbl, exist_ok=True)

#80% of the dataset will be split into train 
split_ratio = 0.8

for card in os.listdir(src): #Looping through each card subfolder in augmented folder
    #Finding the card's folder
    folder = os.path.join(src, card)
    files = [f for f in os.listdir(folder) if f.endswith(".jpg")] #Looping through each image in the card's folder
    #Finding the number to split
    split = int(len(files) * split_ratio)
    #80% into train, 20% into validation
    train_files = files[:split]
    val_files = files[split:]
    #For each image file in train 
    for file in train_files:
        #Taking each image's path and label path
        img_src = os.path.join(folder, file) 
        txt_src = os.path.join(folder, file.replace(".jpg", ".txt"))
        #Copying the image and label into the YOLO dataset
        new_name = "%s_%s" % (card, file) #Since each subfolder has an the same name of images to prevent overriding each image we rename it with the card name
        shutil.copy(img_src, os.path.join(train_img, new_name))
        shutil.copy(txt_src, os.path.join(train_lbl, new_name.replace(".jpg", ".txt")))
    
    #For each image file in val
    for file in val_files:
        #Taking each image's path and label path
        img_src = os.path.join(folder, file)
        txt_src = os.path.join(folder, file.replace(".jpg", ".txt"))
        #Copying the image and label into the YOLO dataset
        new_name = "%s_%s" % (card, file) #Since each subfolder has an the same name of images to prevent overriding each image we rename it with the card name
        shutil.copy(img_src, os.path.join(val_img, new_name))
        shutil.copy(txt_src, os.path.join(val_lbl, new_name.replace(".jpg", ".txt")))

print("YOLO dataset prepared.")