import sys
sys.path.append('/raid/home/geeta/geeta/LogBERT_IDS')
from train_logbert import train_logbert

if __name__ == '__main__':
    train_logbert('/raid/home/geeta/geeta/temp/normal_train.log', epochs=15, batch_size=32)
