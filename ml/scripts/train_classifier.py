import torch
import torch.nn as nn #Neural network tool
import torch.optim as optim
from torchvision import datasets
from torchvision import transforms
from torchvision import models
from torch.utils.data import DataLoader
import json

#Checks if the device has a NVIDIA/CUDA (this will be faster) but defaults to the cpu since I don't have either
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#Transform (the image is resized to 224 by 224 and converted to a tensor so math operations can be done on it)
transform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])

#Datasets (automatically assigns labels based on the folder names)
train_dataset = datasets.ImageFolder("ml/data/classifier_dataset/train", transform=transform)
val_dataset = datasets.ImageFolder("ml/data/classifier_dataset/val", transform=transform)

#Saving the class names 
class_names = train_dataset.classes

with open("ml/models/class_names.json", "w") as f:
    json.dump(class_names, f)

#Loaders (serves the images to the model in groups of 16 at a time)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

#Model
model = models.resnet18(pretrained=True) #Loads a pretained model (ResNet18) which can already recongise shapes and textures
num_classes = len(train_dataset.classes) #Counts the amount of folders in train classifier
model.fc = nn.Linear(model.fc.in_features, num_classes) #Ensuring ResNet18 predicts only the classes specified to it
model = model.to(device) #This moves the entire neural network to device

#Loss (Criterion measures how wrong the model's guesses are)
criterion = nn.CrossEntropyLoss()

#Optimizer (Adam, the logic that updates the model's weights to make it more accurate over time)
optimizer = optim.Adam(model.parameters(), lr=0.001)

#Training (running through the entire dataset 10 times)
epochs = 10

for epoch in range(epochs): #Looping through each epoch (training images)
    #The model enters training
    model.train()
    #Intialising running_loss
    running_loss = 0
    #Looping through 16 images and their labels
    for imgs, labels in train_loader:
        #Moves the images and labels to device
        imgs = imgs.to(device)
        labels = labels.to(device)
        #Cleans the math from the previous guess
        optimizer.zero_grad()
        #The model looks at the image and makes a prediction
        outputs = model(imgs)
        #The loss is a score of how far the prediction was from the actucal label (high = bad prediction)
        loss = criterion(outputs, labels)
        #Working backward from error to figure out which internal neurons were responsible for the mistake
        loss.backward()
        #Makes adjustments to those neurons to ensure the next prediction improves
        optimizer.step()
        #The tally for running_loss shows the error score (to see if the model is improving)
        running_loss += loss.item()

    print("Epoch %d/%d, Loss: %.4f" % (epoch + 1, epochs, running_loss))


#Save model (saving the weights of the trained model into the path)
torch.save(model.state_dict(), "ml/models/card_classifier.pth")

print("Classifier training complete.")