from ultralytics import YOLO

model = YOLO("yolov8n.pt") #The model I am training with (loading the pretained YOLO weights)

model.train(
    data="ml/data/yolo_dataset/dataset.yaml",
    epochs=30,
    imgsz=640,
    batch=8,
    name="card_detector"
)