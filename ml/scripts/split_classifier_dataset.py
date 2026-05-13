import os
import random
import shutil

#Paths
src = "ml/data/classifier_augmented"
train = "ml/data/classifier_dataset/train"
val = "ml/data/classifier_dataset/val"
#Making sure the paths exist (if they don't creating them)
os.makedirs(train, exist_ok=True)
os.makedirs(val, exist_ok=True)

#Splitting the dataset
for card in os.listdir(src): #Looping through each card in the classifier_augmented folder
    #Listing all the images for that card in that folder
    imgs = os.listdir(os.path.join(src, card))
    #Randomising the order of the imgs (to avoid biased training)
    random.shuffle(imgs)
    #An index for 80% of those images
    split = int(0.8 * len(imgs))
    #First 80% are designated for training 
    train_imgs = imgs[:split]
    #The other 20% are designated for validation
    val_imgs = imgs[split:]
    #Making a subfolder for each card in train/val
    os.makedirs(os.path.join(train, card), exist_ok=True)
    os.makedirs(os.path.join(val, card), exist_ok=True)

    #For each img in train
    for img in train_imgs:
        shutil.copy(os.path.join(src, card, img), os.path.join(train, card, img)) #Copying the images from src to train

    #For each img in val
    for img in val_imgs:
        shutil.copy(os.path.join(src, card, img), os.path.join(val, card, img)) #Copying the images from src to val

print("Classifier split complete.")