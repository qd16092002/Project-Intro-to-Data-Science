from transformers import T5EncoderModel, T5Config

import torch
from torch import nn
from torch.nn import functional as tf

import math


class AttentionPooling(nn.Module):
    def __init__(self, concatenated_size, input_size):
        super(AttentionPooling, self).__init__()
        self.proj = nn.Linear(concatenated_size, input_size)
        self.attention = nn.Linear(input_size, 1)
        self.scaling = math.sqrt(input_size)
        self.out_proj = nn.Linear(input_size, input_size)

    def forward(self, x, attention_mask=None):
        # x shape: [batch_size, seq_len, input_size]
        x = self.proj(x)
        scores = self.attention(x)
        scores = scores / self.scaling

        if attention_mask is not None:
          attention_mask = (
              1.0 - attention_mask[:, :, None].to(dtype=torch.float32)) * torch.finfo(torch.float32).min
          scores = scores + attention_mask

        attention_weights = tf.softmax(scores, dim=1)
        # attention_weights shape: [batch_size, seq_len, 1]
        pool_output = torch.sum(attention_weights * x, dim=1)
        # output shape: [batch_size, input_size]
        output = self.out_proj(pool_output)
        return output


class RegressionLayer(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(RegressionLayer, self).__init__()

        self.hidden_proj = nn.Linear(input_size, hidden_size)
        self.output_proj = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = tf.gelu(self.hidden_proj(x))
        x = self.output_proj(x)
        return x
    

class TimeEmbedding(nn.Module):
    def __init__(self, num_months, num_years, embedding_size):
        super(TimeEmbedding, self).__init__()
        self.month_embedding = nn.Embedding(num_months, embedding_size)
        self.year_embedding = None # nn.Embedding(num_years, embedding_size)

    def forward(self, time_input):
        month, _ = torch.split(time_input, 1, dim=1)
        month_embed = self.month_embedding(month)
        return month_embed.squeeze(1)


class EstatePricePredictionModel(nn.Module):
    def __init__(self, pretrained_model_name):
        super(EstatePricePredictionModel, self).__init__()

        self.base_model = T5EncoderModel.from_pretrained(pretrained_model_name, output_hidden_states=True)
        self.time_embedding = TimeEmbedding(12, 50, 768)
        self.pooler = AttentionPooling(768*2, 768)
        self.regression_layer = RegressionLayer(768, 768*2, 1)

    def forward(self, input_ids, time_input, attention_mask):
        encoder_outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
        time_embedding = self.time_embedding(time_input)
        x = encoder_outputs.hidden_states[-2:]
        x = torch.cat([x[0], x[1]], dim=-1)
        x = self.pooler(x, attention_mask)
        added_embedding = tf.gelu(x + time_embedding)
        logits = self.regression_layer(added_embedding)
        return logits
  

class PretrainedEstatePricePredictionModel(nn.Module):
    def __init__(self, config):
        super(PretrainedEstatePricePredictionModel, self).__init__()
        self.base_model = T5EncoderModel(config=config)
        self.time_embedding = TimeEmbedding(12, 50, 768)
        self.pooler = AttentionPooling(768*2, 768)
        self.regression_layer = RegressionLayer(768, 768*2, 1)

    def forward(self, input_ids, time_input, attention_mask):
        encoder_outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
        time_embedding = self.time_embedding(time_input)
        x = encoder_outputs.hidden_states[-2:]
        x = torch.cat([x[0], x[1]], dim=-1)
        x = self.pooler(x, attention_mask)
        added_embedding = tf.gelu(x + time_embedding)
        logits = self.regression_layer(added_embedding)
        return logits


def load_pretrained_model(config_path, state_dict_path: str, device: torch.device | str):
    config = T5Config.from_pretrained(config_path)
    config.output_hidden_states = True

    model = PretrainedEstatePricePredictionModel(config).to(device)
    if state_dict_path is not None and isinstance(state_dict_path, str):
        model.load_state_dict(torch.load(state_dict_path, map_location=device))

    model.eval()

    return model
