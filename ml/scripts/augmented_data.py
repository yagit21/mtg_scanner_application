from torchvision import transforms #PyTorch image augmentation tool
from PIL import Image #To handle images
import os
import random
import numpy as np #Using numpy arrays since OpenCV works with arrays
from tqdm import tqdm 
import cv2 #OpenCV library

#Paths
base_dir = os.path.dirname(__file__)  #This is ml/scripts
data_dir = os.path.join(base_dir, "../data")

input_root = os.path.join(data_dir, "card_images")
output_root = os.path.join(data_dir, "augmented") #This is where the augmented cards go
background_dir = os.path.join(data_dir, "backgrounds")

os.makedirs(output_root, exist_ok=True)

#Generate cards with different camera/card angles
#def perspective_warp(pil_img):
    # img = np.array(pil_img) #This transforms the image into a martix of pixels
    # h, w = img.shape[:2] #Getting the image size (height and width)
    # #This is the original corner of the card (top-left, top-right, bottom-left, bottom-right)
    # pts1 = np.float32([[0,0],[w,0],[0,h],[w,h]])
    # shift = 0.15 * w
    # #This is the new distorted corners the card is assigned with random shifts
    # pts2 = np.float32([
    #     [random.uniform(0, shift), random.uniform(0, shift)],
    #     [w-random.uniform(0, shift), random.uniform(0, shift)],
    #     [random.uniform(0, shift), h-random.uniform(0, shift)],
    #     [w-random.uniform(0, shift), h-random.uniform(0, shift)]
    # ])
    # #This uses openCV to calculate how each pixel moves
    # matrix = cv2.getPerspectiveTransform(pts1, pts2)
    # #This bends the image to simulate an angled camera, titlted card, etc
    # warped = cv2.warpPerspective(img, matrix, (w, h))

    # return Image.fromarray(warped)

#Partially hidden cards
# def add_occlusion(pil_img):
#     #Transforming the image and getting its size
#     img = np.array(pil_img)
#     h, w = img.shape[:2]
#     #Giving randomised width and height of the opaque part placed over the image 
#     occ_w = random.randint(30, 100)
#     occ_h = random.randint(30, 100)
#     #Assigning the patch a random location
#     x = random.randint(0, w - occ_w)
#     y = random.randint(0, h - occ_h)
#     #Generating a random colour value (helps the model become indifferent to the appearance of the object)
#     colour = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
#     #This function draws a box size of occ_w and occ_h that overwrites the image pixel data (the thickness parameter [-1] makes the function draw a filled rectangle)
#     cv2.rectangle(img, (x,y), (x+occ_w,y+occ_h), colour, -1)

#     return Image.fromarray(img)

#Creating different lightings
def add_shadow(img, x, y, w, h):
    #Duplicating the image so I can make changes on the copy 
    overlay = img.copy()
    #The colour of the shadow
    shadow_colour = (0, 0, 0)
    #How far the shadow is in the rectangle
    shadow_offset = random.randint(5, 15)
    #Drawing the rectangle over the overlay copy, 
    cv2.rectangle(
        overlay,
        (x + shadow_offset, y + shadow_offset), #This ensures the shadow is at the bottom right of the original image
        (x + w + shadow_offset, y + h + shadow_offset), 
        shadow_colour,
        -1 #Fills the rectnagle
    )
    #Choosing a random transparency level between 8% to 18%
    alpha = random.uniform(0.08, 0.18)
    #Blends the overlay with the original image (since the alpha is low the result is a faint shadow)
    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

def add_background(pil_img):

    bg_files = os.listdir(background_dir) #List of all the background images in the background file
    #Picking a random background image
    bg_path = os.path.join(background_dir, random.choice(bg_files))
    bg = Image.open(bg_path).convert("RGB") #Converting the image to an RGB format
    #Resizing the image to 640 by 640
    bg = bg.resize((640, 640))
    #Converting the background to a numpy array
    bg_np = np.array(bg)
    #Converting the card image to a numpy array
    card = np.array(pil_img)

    #Scaling the card randomly between 40% and 90% of the original size (to simulate different distances)
    scale = random.uniform(0.4, 0.9)
    card_w = int(224 * scale)
    card_h = int(320 * scale)
    #Resizing the image
    card = cv2.resize(card, (card_w, card_h))

    #Keep entire card onscreen
    x_offset = random.randint(0, 640 - card_w)
    y_offset = random.randint(0, 640 - card_h)
    
    #Applying a random transparency between 88% to 98%
    alpha = random.uniform(0.88, 0.98)
    #Adding shadow to the card
    bg_np = add_shadow(bg_np, x_offset, y_offset, card_w, card_h)
    #Rotating the card randomly between -10 and 10 degrees
    angle = random.uniform(-10, 10)
    #Using the center of the card to pivot rotation
    center = (card_w // 2, card_h // 2)
    #Using the cv2 getRotationMatrix2D to define the rotation (the 1.0 keeps the image 100% of the original size)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    #Applying the martix to the card (to ensure no empty spaces at the border after rotation cv2.BORDER_REPLICATE is used which fills empty spaces using the same border colour as the card)
    #card = cv2.warpAffine(card, matrix, (card_w, card_h), borderMode=cv2.BORDER_REPLICATE)
    
    #Calculating the new boundary coordinates to ensure they stay within the 640 by 640 limit (ensuring the starting points aren't top-left and the ending points aren't bottom-right)
    x1 = max(0, x_offset)
    y1 = max(0, y_offset)
    x2 = min(640, x_offset + card_w)
    y2 = min(640, y_offset + card_h)
    #This extracts the rotated and reshaped region of the card from numpy card image
    card_crop = card[y1 - y_offset:y2 - y_offset, x1 - x_offset:x2 - x_offset]
    region = bg_np[y1:y2, x1:x2]
    #Blends the two images together using the alpha value
    blended = cv2.addWeighted(region, 1 - alpha, card_crop, alpha, 0)
    bg_np[y1:y2, x1:x2] = blended #Replaces the background with the new blended image

    box_w = x2 - x1
    box_h = y2 - y1

    x_center = ((x1 + x2) / 2) / 640
    y_center = ((y1 + y2) / 2) / 640

    w = box_w / 640
    h = box_h / 640
    
    #Applying a slight Gaussian blur
    bg_np = cv2.GaussianBlur(bg_np, (3,3), 0)

    #Webcam noise (0 is the center of the noise, while 8 is the spread of the noise)(bg_npshap ensures the noise is the same size as the image)(.astype(np.int16) allows for negative values - noise can either darken or brighten pixels)
    noise = np.random.normal(0, 8, bg_np.shape).astype(np.int16)
    #Converts the image pixel values to int16
    bg_np = bg_np.astype(np.int16)
    #Adding noise to the image pixels and ensures that is stays between 0-255 range (then converts the image pixels back to uint8 which is the format for PIL and OpenCV)
    bg_np = np.clip(bg_np + noise, 0, 255).astype(np.uint8)
    #Converting the NumPy array of the image back into a PIL image and returning it with its bounding box coordinates
    return Image.fromarray(bg_np), [x_center, y_center, w, h]

# def random_crop(pil_img):
#     #Getting the img as a numpy arrary
#     img = np.array(pil_img)
#     h, w = img.shape[:2] #Image dimensions
#     #Picking a random horizontal/vertical crop point (limited to max 25% of the image's original height/width)
#     crop_x = random.randint(0, int(w * 0.25))
#     crop_y = random.randint(0, int(h * 0.25))
#     #Using numpy slicing to crop the image to the new point coordinates
#     cropped = img[crop_y:h, crop_x:w]
#     #Converting the image back into a pillow object
#     return Image.fromarray(cropped)

transform = transforms.Compose([   
    transforms.ColorJitter(
        brightness=0.4, contrast=0.4, saturation=0.3, hue=0.1), #Randomly adjustes the brightness, contrast, saturation, and hue to simulate different lighting conditions
    
    transforms.RandomAdjustSharpness(
        sharpness_factor=2, p=0.3 #30% chance the sharpness increases by a factor of 2
    )
])


aug_per_img = 40  #We will multiply each image by 40 

for card in os.listdir(input_root): #For each card in card_images folder
    in_path = os.path.join(input_root, card)
    out_path = os.path.join(output_root, card) #Defining the path for the card, in augmented folder and the augmented images of a card will be kept in the card subfolder
    
    os.makedirs(out_path, exist_ok=True) #Making sure the path exists, if not is created
    
    img = Image.open(os.path.join(in_path, "img_0.jpg")).convert("RGB")
    #Runing the augmentation process 40 times for each original image
    for i in range(aug_per_img):
        aug_img = transform(img) #Applying transformations

        #Add different backgrounds
        aug_img, bbox = add_background(aug_img)

        #Save augmented image
        img_path = os.path.join(out_path, "img_%s.jpg" % (i)) 
        aug_img.save(img_path)

        #Save YOLO label file in YOLO format
        label_path = os.path.join(out_path, "img_%s.txt" % (i))
        #0 represents the class ID and the boundary box dimensions
        with open(label_path, "w") as f:
            f.write("0 %s %s %s %s\n" % (bbox[0], bbox[1], bbox[2], bbox[3]))
        
        print("Saving %s" % (img_path))
    
print("Done.")

