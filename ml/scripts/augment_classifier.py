
from torchvision import transforms
from PIL import Image
import os

#Paths
input_root = "ml/data/card_images"
output_root = "ml/data/classifier_augmented"

os.makedirs(output_root, exist_ok=True)

#Simpler augmentations
transform = transforms.Compose([
    transforms.RandomRotation(15), #Rotating the image max 15 dgrees
    transforms.ColorJitter(brightness=0.3, contrast=0.3), #Randomly changing brightness and contrast up to 30%
    transforms.RandomResizedCrop(224,scale=(0.9, 1.0)), #Crops a random section of the image and resizes it to 224 by 224 pixels
    transforms.GaussianBlur(3) #Applying a slight blur
])

aug_per_img = 40 

for card in os.listdir(input_root): #Looping through each card
    
    in_path = os.path.join(input_root, card)
    out_path = os.path.join(output_root, card)
    #Creating (or making sure the location exists)
    os.makedirs(out_path, exist_ok=True)
    #Opens the img of the card saved in the folder and converts it to an RGB
    img = Image.open(os.path.join(in_path, "img_0.jpg")).convert("RGB")
    #Generating 40 modified versions of the image
    for i in range(aug_per_img):
        aug_img = transform(img) #Applying the transformations
        aug_img.save(os.path.join(out_path, "img_%s.jpg" % (i))) #Saving the image to the classifer_augmented folder
    
    print("%s complete." % (card))

print("Classifier dataset complete.")