from torchvision import transforms
from PIL import Image
import os

#Paths
input_root = "ml/data/realistic_cards"
output_root = "ml/data/classifier_augmented"

os.makedirs(output_root, exist_ok=True)

#Better augmentations for MTG cards
transform = transforms.Compose([

    #Small realistic rotation
    transforms.RandomRotation(10),

    #Perspective distortion
    transforms.RandomPerspective(distortion_scale=0.12, p=0.4),

    #Small movement/zoom changes
    transforms.RandomAffine(degrees=5, translate=(0.03, 0.03), scale=(0.95, 1.05)),

    #Mild lighting changes
    transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),

    #Keep full card visible
    transforms.Resize((224, 224)),

    #Mild camera blur
    transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 0.8))
])

#Small number since I now have multiple photo
aug_per_img = 60

#Loop through each card folder
for card in os.listdir(input_root):

    card_input_path = os.path.join(input_root, card)

    #Skip non-folders
    if not os.path.isdir(card_input_path):
        continue

    card_output_path = os.path.join(output_root, card)
    os.makedirs(card_output_path, exist_ok=True)

    img_counter = 0

    #Loop through every real image
    for img_name in os.listdir(card_input_path):

        if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img_path = os.path.join(card_input_path, img_name)

        try:
            img = Image.open(img_path).convert("RGB")

            #Save original resized image too
            original = img.resize((224, 224))
            original.save(os.path.join(card_output_path, "img_%s.jpg" % (img_counter)))

            img_counter += 1

            #Generate augmentations
            for i in range(aug_per_img):
                aug_img = transform(img)
                aug_img.save(os.path.join(card_output_path, "img_%s.jpg" % (img_counter)))
                img_counter += 1

        except Exception as e:
            print("Error processing %s: %s" % (img_path, e))

    print("%s complete." % (card))

print("Classifier dataset complete.")