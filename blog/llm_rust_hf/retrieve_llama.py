import torch
from transformers import AutoModelForCausalLM, LlamaConfig, PreTrainedTokenizerFast


def report(y, layer):
    print(f"Class: {type(layer)}")
    print(f"First: {round(y.flatten()[0].item(), 6):.6f}")
    print(f"Shape: {list(y.shape)}")
    print(f"Min: {round(y.min().item(), 6):.6f}")
    print(f"Max: {round(y.max().item(), 6):.6f}")
    print(f"Mean: {round(y.mean().item(), 6):.6f}")


def generate_pseudo_input():
    seq_len = 10
    hidden_size = 2048
    value = 0.5
    x = torch.full((1, seq_len, hidden_size), value)
    pos_ids = torch.tensor(range(seq_len)).view(1, seq_len)
    return x, pos_ids


def retrieve_llama_mlp(model, layer_idx=0):
    layer = model.model.layers[layer_idx].mlp
    x, _ = generate_pseudo_input()
    y = layer(x)
    report(y, layer)


def retrieve_llama_attention(model, layer_idx=0):
    layer = model.model.layers[layer_idx].self_attn
    x, pos_ids = generate_pseudo_input()
    y = layer(x, position_ids=pos_ids)[0]
    report(y, layer)


def retrieve_llama_decoder_layer(model, layer_idx=0):
    layer = model.model.layers[layer_idx]
    x, pos_ids = generate_pseudo_input()
    y = layer(x, position_ids=pos_ids)[0]
    report(y, layer)


def retrieve_tokens(model, tokenizer):
    input_text = "Who was the first president of the United States?"
    input_tokens = tokenizer(input_text, return_tensors="pt")
    output_tokens = model.generate(input_tokens.input_ids, max_new_tokens=3)[0]
    print(f"Tokens: {output_tokens.tolist()}")
    print(f"Text: {repr(tokenizer.decode(output_tokens))}")


if __name__ == "__main__":
    config = LlamaConfig.from_pretrained("./Llama-3.2-1B-Instruct/config.json")
    model = AutoModelForCausalLM.from_pretrained(
        "./Llama-3.2-1B-Instruct/model.safetensors", config=config
    )
    tokenizer = PreTrainedTokenizerFast(
        tokenizer_file="./Llama-3.2-1B-Instruct/tokenizer.json"
    )
    retrieve_llama_mlp(model)
    retrieve_llama_attention(model)
    retrieve_llama_decoder_layer(model)
    retrieve_tokens(model, tokenizer)
