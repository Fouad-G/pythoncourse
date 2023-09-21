import torch
from torch.utils.data import DataLoader
from device import DEVICE
from transform import training_transform_64, validation_transform_64
from dataset import CatsDogsDataSet, TRAIN_SET_FOLDER
import numpy as np
from network import Network
from trainloop import Trainer

class Trainer2(Trainer):
    def __init__(self, network, loss_function, chkpt_path):
      super().__init__(network, loss_function)

      self.ep = 0
      self.chkpt_path = chkpt_path
      self.best_val_acc = 0
      try:
          chkpt = torch.load(self.chkpt_path)
          self.network.load_state_dict(chkpt["net_state_dict"])
          self.optim.load_state_dict(chkpt["optim_state_dict"])
          self.scheduler.load_state_dict(chkpt["scheduler_state_dict"])
          self.best_val_acc = chkpt["best_val_acc"]
          self.ep = chkpt["epoch"]
      except:
          print("Could not find checkpoint, starting from scratch")

    def train(self, loader_train, loader_val):
      while True:
        train_loss, train_acc = self.epoch(loader_train, True, self.ep)
        val_loss, val_acc = self.epoch(loader_val, False, self.ep)
        self.scheduler.step()
        
        self.ep += 1

        if val_acc > self.best_val_acc:
          self.best_val_acc = val_acc
          print("Validation accuracy is best, saving checkpoint")
          torch.save({
              "net_state_dict": self.network.state_dict(),
              "optim_state_dict": self.optim.state_dict(),
              "scheduler_state_dict": self.scheduler.state_dict(),
              "best_val_acc": self.best_val_acc,
              "epoch": self.ep
          }, self.chkpt_path)

if __name__ == "__main__":
    dataset = CatsDogsDataSet(TRAIN_SET_FOLDER, max_samples_per_class=None, transform=training_transform_64, is_validation=False)
    dataset_val = CatsDogsDataSet(TRAIN_SET_FOLDER, max_samples_per_class=None, transform=validation_transform_64, is_validation=True)
    
    dataloader = DataLoader(dataset, batch_size=200, shuffle=True)
    dataloader_val = DataLoader(dataset_val, batch_size=200, shuffle=True)
    
    net = Network().to(DEVICE)
    loss = torch.nn.CrossEntropyLoss()

    trainer = Trainer2(net, loss, "model.pt")
    trainer.train(dataloader, dataloader_val)
        