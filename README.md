# toric-RL-decoder

![](src/toric_code_gif.gif)
<p align="center">
    <iframe src="https://giphy.com/embed/S5h6wEu0LBE13X22s8" width="480" height="360" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/S5h6wEu0LBE13X22s8">via GIPHY</a></p>
</p>

Deep reinforcement learning decoder for the toric code

## Prerequisites 
- Python 3

## Getting started 
### Installation 
- The required libraries are matplotlib, numpy and pytorch (add all requirements!)

```bash
pip install -r requirements.txt
```

- Clone this repo:
```bash
git clone https://github.com/mats-granath/toric-RL-decoder.git
```

## How to use the simulator
There are two example scripts
- train_script.py
- prediction_script.py

The train script trains an agent to solve syndromes. All the hyperparameters related to the training are specified in the script. Moreover, an evaluation of the training run is stored in the data folder with a timestamp.

The predict script uses a trained network and predicts given a specified amount of syndromes. The trained network can be loaded from the network folder.


