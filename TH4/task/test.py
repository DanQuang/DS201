import torch
import os
from tqdm.auto import tqdm
from model import ResNet50, VGG19, VGG16
from data_utils import load_data
from evaluate import evaluate

class Test_Task:
    def __init__(self, config):
        self.save_path = config["save_path"]
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.num_classes = config["num_classes"]
        self.model_name = config["model"]
        if self.model_name == "ResNet50":
            self.model = ResNet50.ResNet50(config).to(self.device)
        elif self.model_name == "VGG19":
            self.model = VGG19.VGG19(config).to(self.device)
        elif self.model_name == "VGG16":
            self.model = VGG16.VGG16(config).to(self.device)
        self.dataloader = load_data.Load_Data(config)

    def predict(self):
        test = self.dataloader.load_test()
        best_model = f"{self.model_name}_best_model.pth"

        if os.path.join(self.save_path, best_model):
            checkpoint = torch.load(os.path.join(self.save_path, best_model))
            self.model.load_state_dict(checkpoint["model_state_dict"])

            test_trues = []
            test_preds = []
            self.model.eval()
            with torch.inference_mode():
                for _, item in enumerate(tqdm(test)):
                    X, y = item["image"].to(self.device), item["label"].to(self.device)
                    test_trues += y.tolist()
                    y_logits = self.model(X)
                    y_preds = torch.softmax(y_logits, dim = 1).argmax(dim= 1)
                    test_preds += y_preds.tolist()

                acc, prec, recall, f1 = evaluate.compute_score(test_trues, test_preds)

                print(f"test acc: {acc:.4f} | test f1: {f1:.4f} | test precision: {prec:.4f} | test recall: {recall:.4f}")

        else:
            print(f"Chưa train model {self.model_name}!!")
