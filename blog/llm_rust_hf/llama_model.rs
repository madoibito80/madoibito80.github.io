use crate::config;
use crate::llama_decoder_layer::LlamaDecoderLayer;
use crate::util;
use candle_core::{Module, Tensor};
use candle_nn::{Embedding, Linear, RmsNorm};
use safetensors::tensor::SafeTensors;
use tokenizers::tokenizer::{Result, Tokenizer};

pub struct LlamaModel {
    embed_tokens: Embedding,
    layers: Vec<LlamaDecoderLayer>,
    norm: RmsNorm,
    lm_head: Linear,
}

// Inspired by the implementation in Hugging Face Transformers:
// https://github.com/huggingface/transformers/blob/v4.45.0/src/transformers/models/llama/modeling_llama.py#L883
// https://github.com/huggingface/transformers/blob/v4.45.0/src/transformers/models/llama/modeling_llama.py#L1105
impl LlamaModel {
    pub fn new(safetensors: SafeTensors) -> Result<Self> {
        let embed_tokens_weight = Tensor::from_slice(
            &util::convert_bytes_to_bf16(&safetensors.tensor("model.embed_tokens.weight")?.data()),
            safetensors.tensor("model.embed_tokens.weight")?.shape(),
            &config::DEVICE,
        )?
        .to_dtype(config::FORWARD_DTYPE)?;
        let embed_tokens = Embedding::new(embed_tokens_weight.clone(), config::HIDDEN_SIZE);
        let lm_head = Linear::new(embed_tokens_weight.clone(), None);

        let mut layers = Vec::new();

        for i in 0..config::NUM_HIDDEN_LAYERS {
            let llama_decoder_layer = LlamaDecoderLayer::new(
                &safetensors.tensor(&format!("model.layers.{}.self_attn.q_proj.weight", i))?,
                &safetensors.tensor(&format!("model.layers.{}.self_attn.k_proj.weight", i))?,
                &safetensors.tensor(&format!("model.layers.{}.self_attn.v_proj.weight", i))?,
                &safetensors.tensor(&format!("model.layers.{}.self_attn.o_proj.weight", i))?,
                &safetensors.tensor(&format!("model.layers.{}.mlp.gate_proj.weight", i))?,
                &safetensors.tensor(&format!("model.layers.{}.mlp.up_proj.weight", i))?,
                &safetensors.tensor(&format!("model.layers.{}.mlp.down_proj.weight", i))?,
                &safetensors.tensor(&format!("model.layers.{}.input_layernorm.weight", i))?,
                &safetensors.tensor(&format!(
                    "model.layers.{}.post_attention_layernorm.weight",
                    i
                ))?,
            )?;
            layers.push(llama_decoder_layer);
        }

        let norm = RmsNorm::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&safetensors.tensor("model.norm.weight")?.data()),
                safetensors.tensor("model.norm.weight")?.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            config::RMS_NORM_EPS,
        );
        Ok(Self {
            embed_tokens,
            layers,
            norm,
            lm_head,
        })
    }

    pub fn forward(&self, ids: &Tensor, pos_idx: usize) -> Result<Tensor> {
        let mut h = self.embed_tokens.forward(&ids)?;
        let (seq_len, _) = h.dims2()?;
        h = h.reshape(&[1, seq_len, config::HIDDEN_SIZE])?;
        for i in 0..config::NUM_HIDDEN_LAYERS {
            h = self.layers[i].forward(&h, pos_idx)?;
        }
        h = self.norm.forward(&h)?;
        let logit = self.lm_head.forward(&h)?;
        let id = logit.get(0)?.get(seq_len - 1)?.argmax(0)?;
        Ok(id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_llama_model() -> Result<()> {
        let file_path = "../Llama-3.2-1B-Instruct/model.safetensors";
        let file_data = std::fs::read(file_path)?;
        let safetensors = SafeTensors::deserialize(&file_data)?;
        let llama_model = LlamaModel::new(safetensors)?;

        let tokenizer = Tokenizer::from_file("../Llama-3.2-1B-Instruct/tokenizer.json")?;
        let encoded =
            tokenizer.encode("Who was the first president of the United States?", false)?;
        let prefix = Tensor::new(&[config::BOS_TOKEN_ID], &config::DEVICE)?;
        let mut ids = Tensor::new(encoded.get_ids(), &config::DEVICE)?;
        ids = Tensor::cat(&[&prefix, &ids], 0)?;

        let max_new_tokens: usize = 3;
        for _ in 0..max_new_tokens {
            let id_next = llama_model.forward(&ids, 0)?.reshape(&[1])?;
            ids = Tensor::cat(&[&ids, &id_next], 0)?;
        }

        let decoded = tokenizer.decode(&ids.to_vec1()?, false)?;
        println!("Tokens: {:?}", &ids.to_vec1::<u32>()?);
        println!("Text: {:?}", decoded);
        Ok(())
    }
}
