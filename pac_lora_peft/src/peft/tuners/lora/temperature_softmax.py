"""
@File        :   temperature_softmax.py
@Description :   Softmax with temperature
@Author      :   Jinghui Zhang
@Time        :   2024/12/13
"""

import torch.nn.functional as F
import torch.nn

class TemperatureSoftmax(torch.nn.Module):
    def __init__(self, temperature=0.1):
        super(TemperatureSoftmax, self).__init__()
        self.temperature = temperature

    def forward(self, x):
        return F.softmax(x / self.temperature, dim=-1)