import torch
from datetime import datetime


def transform_input(tokenizer, input_dict, device=None):
    if device is None:
        device = torch.device("cpu")
    input_text = f"Loại: {input_dict['estate_type']}{tokenizer.eos_token}Diện tích: {float(input_dict['square'])}{tokenizer.eos_token}Vị trí: {input_dict['address']}{tokenizer.eos_token}Mô tả: {input_dict['description']}"
    present_month = datetime.now().month - 1
    present_year = datetime.now().year - 2000
    time_input = torch.tensor([[present_month, present_year]], dtype=torch.int64)
    batch_encoding = tokenizer(input_text, return_tensors="pt")
    batch_encoding["time_input"] = time_input
    
    return batch_encoding.to(device)


def predict_price(model, scaler, input_encoding):
    with torch.no_grad():
        logits = model(input_encoding["input_ids"], input_encoding["time_input"], input_encoding["attention_mask"])
    
    prices = scaler.invert_transform(logits.cpu().numpy())
    return prices.item()
