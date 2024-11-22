use crate::config;
use crate::llama_attention::LlamaAttention;
use crate::llama_mlp::LlamaMLP;
use crate::util;
use candle_core::{Module, Result, Tensor};
use candle_nn::RmsNorm;
use safetensors::tensor::{SafeTensors, TensorView};

pub struct LlamaDecoderLayer {
    self_attn: LlamaAttention,
    mlp: LlamaMLP,
    input_layernorm: RmsNorm,
    post_attention_layernorm: RmsNorm,
}

// Inspired by https://github.com/huggingface/transformers/blob/v4.45.0/src/transformers/models/llama/modeling_llama.py#L679
impl LlamaDecoderLayer {
    pub fn new(
        q_proj_weight: &TensorView,
        k_proj_weight: &TensorView,
        v_proj_weight: &TensorView,
        o_proj_weight: &TensorView,
        gate_proj_weight: &TensorView,
        up_proj_weight: &TensorView,
        down_proj_weight: &TensorView,
        input_layernorm_weight: &TensorView,
        post_attention_layernorm_weight: &TensorView,
    ) -> Result<Self> {
        let self_attn =
            LlamaAttention::new(q_proj_weight, k_proj_weight, v_proj_weight, o_proj_weight)?;
        let mlp = LlamaMLP::new(gate_proj_weight, up_proj_weight, down_proj_weight)?;
        let input_layernorm = RmsNorm::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&input_layernorm_weight.data()),
                input_layernorm_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            config::RMS_NORM_EPS,
        );
        let post_attention_layernorm = RmsNorm::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&post_attention_layernorm_weight.data()),
                post_attention_layernorm_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            config::RMS_NORM_EPS,
        );
        Ok(Self {
            self_attn,
            mlp,
            input_layernorm,
            post_attention_layernorm,
        })
    }

    pub fn forward(&self, x: &Tensor, pos_idx: usize) -> Result<Tensor> {
        let h1 = self.input_layernorm.forward(x)?;
        let h1 = (self.self_attn.forward(&h1, pos_idx)? + x)?;
        let h2 = self.post_attention_layernorm.forward(&h1)?;
        let h2 = (self.mlp.forward(&h2)? + h1)?;
        Ok(h2)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_llama_decoder_layer() -> Result<()> {
        let file_path = "../Llama-3.2-1B-Instruct/model.safetensors";
        let file_data = std::fs::read(file_path)?;
        let safetensors = SafeTensors::deserialize(&file_data)?;
        let llama_decoder_layer = LlamaDecoderLayer::new(
            &safetensors.tensor("model.layers.0.self_attn.q_proj.weight")?,
            &safetensors.tensor("model.layers.0.self_attn.k_proj.weight")?,
            &safetensors.tensor("model.layers.0.self_attn.v_proj.weight")?,
            &safetensors.tensor("model.layers.0.self_attn.o_proj.weight")?,
            &safetensors.tensor("model.layers.0.mlp.gate_proj.weight")?,
            &safetensors.tensor("model.layers.0.mlp.up_proj.weight")?,
            &safetensors.tensor("model.layers.0.mlp.down_proj.weight")?,
            &safetensors.tensor("model.layers.0.input_layernorm.weight")?,
            &safetensors.tensor("model.layers.0.post_attention_layernorm.weight")?,
        )?;

        let shape = (1, 10, config::HIDDEN_SIZE);
        let x = Tensor::full(0.5, shape, &config::DEVICE)?.to_dtype(config::FORWARD_DTYPE)?;
        let y = llama_decoder_layer
            .forward(&x, 0)?
            .to_dtype(candle_core::DType::F32)?;

        let y_first = y.flatten_all()?.get(0)?.to_scalar::<f32>()?;
        let y_shape = y.shape().dims();
        let y_min = y.flatten_all()?.min(0)?.to_scalar::<f32>()?;
        let y_max = y.flatten_all()?.max(0)?.to_scalar::<f32>()?;
        let y_mean = y.flatten_all()?.mean(0)?.to_scalar::<f32>()?;

        println!("First: {:?}", y_first);
        println!("Shape: {:?}", y_shape);
        println!("Min: {:?}", y_min);
        println!("Max: {:?}", y_max);
        println!("Mean: {:?}", y_mean);

        let epsilon = 1e-6;
        assert!((y_first - 0.489133).abs() < epsilon, "Mismatch in y_first");
        assert_eq!(y_shape, &[1, 10, 2048], "Mismatch in y_shape");
        assert!((y_min - 0.378667).abs() < epsilon, "Mismatch in y_min");
        assert!((y_max - 0.635870).abs() < epsilon, "Mismatch in y_max");
        assert!((y_mean - 0.500260).abs() < epsilon, "Mismatch in y_mean");
        Ok(())
    }
}
