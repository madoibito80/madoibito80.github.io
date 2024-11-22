use crate::config;
use crate::util;
use candle_core::{Module, Result, Tensor};
use candle_nn::{rotary_emb, Linear};
use safetensors::tensor::{SafeTensors, TensorView};

pub struct LlamaAttention {
    q_proj: Linear,
    k_proj: Linear,
    v_proj: Linear,
    o_proj: Linear,
}

impl LlamaAttention {
    pub fn new(
        q_proj_weight: &TensorView,
        k_proj_weight: &TensorView,
        v_proj_weight: &TensorView,
        o_proj_weight: &TensorView,
    ) -> Result<Self> {
        let q_proj = Linear::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&q_proj_weight.data()),
                q_proj_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            None,
        );
        let k_proj = Linear::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&k_proj_weight.data()),
                k_proj_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            None,
        );
        let v_proj = Linear::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&v_proj_weight.data()),
                v_proj_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            None,
        );
        let o_proj = Linear::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&o_proj_weight.data()),
                o_proj_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            None,
        );
        Ok(Self {
            q_proj,
            k_proj,
            v_proj,
            o_proj,
        })
    }

    // Inspired by the implementation in candle-transformers:
    // https://github.com/huggingface/candle/blob/0.8.0/candle-transformers/src/models/llama.rs#L260-L263
    // https://github.com/huggingface/candle/blob/0.8.0/candle-transformers/src/models/llama.rs#L160-L201
    fn generate_rotary_emb(&self) -> Result<(Tensor, Tensor)> {
        let low_freq_wavelen = config::rope_scaling::ORIGINAL_MAX_POSITION_EMBEDDINGS as f32
            / config::rope_scaling::LOW_FREQ_FACTOR;
        let high_freq_wavelen = config::rope_scaling::ORIGINAL_MAX_POSITION_EMBEDDINGS as f32
            / config::rope_scaling::HIGH_FREQ_FACTOR;
        let inv_freq: Vec<_> = (0..config::HEAD_DIM)
            .step_by(2)
            .map(|i| 1. / config::ROPE_THETA.powf(i as f32 / config::HEAD_DIM as f32))
            .map(|i| {
                let wavelen = 2. * std::f32::consts::PI / i;
                if wavelen < high_freq_wavelen {
                    i
                } else if wavelen > low_freq_wavelen {
                    i / config::rope_scaling::FACTOR
                } else {
                    let smooth_factor =
                        (config::rope_scaling::ORIGINAL_MAX_POSITION_EMBEDDINGS as f32 / wavelen
                            - config::rope_scaling::LOW_FREQ_FACTOR)
                            / (config::rope_scaling::HIGH_FREQ_FACTOR
                                - config::rope_scaling::LOW_FREQ_FACTOR);
                    (1. - smooth_factor) * i / config::rope_scaling::FACTOR + smooth_factor * i
                }
            })
            .collect();
        let inv_freq = Tensor::new(inv_freq, &config::DEVICE)?.to_dtype(config::FORWARD_DTYPE)?;
        let freqs = Tensor::arange(0, config::MAX_POSITION_EMBEDDINGS as u32, &config::DEVICE)?
            .reshape((config::MAX_POSITION_EMBEDDINGS, 1))?
            .to_dtype(config::FORWARD_DTYPE)?
            .matmul(&inv_freq.reshape((1, inv_freq.elem_count()))?)?;
        let cos = freqs.cos()?;
        let sin = freqs.sin()?;
        Ok((cos, sin))
    }

    // Inspired by https://github.com/huggingface/candle/blob/0.8.0/candle-transformers/src/utils.rs#L24-L36
    fn repeat_kv(&self, x: Tensor, n_rep: usize) -> Result<Tensor> {
        let (b_sz, n_kv_head, seq_len, head_dim) = x.dims4()?;
        Tensor::cat(&vec![&x; n_rep], 2)?.reshape((b_sz, n_kv_head * n_rep, seq_len, head_dim))
    }

    // Inspired by the implementations in Hugging Face Transformers and Candle Transformers:
    // https://github.com/huggingface/transformers/blob/v4.45.0/src/transformers/models/llama/modeling_llama.py#L573
    // https://github.com/huggingface/candle/blob/0.8.0/candle-transformers/src/models/llama.rs#L257
    pub fn forward(&self, x: &Tensor, pos_idx: usize) -> Result<Tensor> {
        let q = self.q_proj.forward(x)?;
        let k = self.k_proj.forward(x)?;
        let v = self.v_proj.forward(x)?;

        let (b_sz, seq_len, _) = x.dims3()?;
        let q = q
            .reshape((b_sz, seq_len, config::NUM_ATTENTION_HEADS, config::HEAD_DIM))?
            .transpose(1, 2)?
            .contiguous()?;
        let k = k
            .reshape((b_sz, seq_len, config::NUM_KEY_VALUE_HEADS, config::HEAD_DIM))?
            .transpose(1, 2)?
            .contiguous()?;
        let v = v
            .reshape((b_sz, seq_len, config::NUM_KEY_VALUE_HEADS, config::HEAD_DIM))?
            .transpose(1, 2)?
            .contiguous()?;

        let (cos, sin) = self.generate_rotary_emb()?;
        let cos = cos.narrow(0, pos_idx, seq_len)?;
        let sin = sin.narrow(0, pos_idx, seq_len)?;

        let q = rotary_emb::rope(&q, &cos, &sin)?;
        let k = rotary_emb::rope(&k, &cos, &sin)?;

        let k = self.repeat_kv(k, config::NUM_ATTENTION_HEADS / config::NUM_KEY_VALUE_HEADS)?;
        let v = self.repeat_kv(v, config::NUM_ATTENTION_HEADS / config::NUM_KEY_VALUE_HEADS)?;

        let att = (q.matmul(&k.transpose(2, 3)?)? / (config::HEAD_DIM as f64).sqrt())?;
        let att = candle_nn::ops::softmax_last_dim(&att)?;
        let y = att.matmul(&v)?;
        let y = y
            .transpose(1, 2)?
            .reshape(&[b_sz, seq_len, config::HIDDEN_SIZE])?;
        let y = self.o_proj.forward(&y)?;
        Ok(y)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_llama_attention() -> Result<()> {
        let file_path = "../Llama-3.2-1B-Instruct/model.safetensors";
        let file_data = std::fs::read(file_path)?;
        let safetensors = SafeTensors::deserialize(&file_data)?;
        let llama_attn = LlamaAttention::new(
            &safetensors.tensor("model.layers.0.self_attn.q_proj.weight")?,
            &safetensors.tensor("model.layers.0.self_attn.k_proj.weight")?,
            &safetensors.tensor("model.layers.0.self_attn.v_proj.weight")?,
            &safetensors.tensor("model.layers.0.self_attn.o_proj.weight")?,
        )?;

        let shape = (1, 10, config::HIDDEN_SIZE);
        let x = Tensor::full(0.5, shape, &config::DEVICE)?.to_dtype(config::FORWARD_DTYPE)?;
        let y = llama_attn
            .forward(&x, 0)?
            .to_dtype(candle_core::DType::F32)?;

        let y_shape = y.shape().dims();
        let y_first = y.flatten_all()?.get(0)?.to_scalar::<f32>()?;
        let y_min = y.flatten_all()?.min(0)?.to_scalar::<f32>()?;
        let y_max = y.flatten_all()?.max(0)?.to_scalar::<f32>()?;
        let y_mean = y.flatten_all()?.mean(0)?.to_scalar::<f32>()?;

        println!("Shape: {:?}", y_shape);
        println!("First: {:?}", y_first);
        println!("Min: {:?}", y_min);
        println!("Max: {:?}", y_max);
        println!("Mean: {:?}", y_mean);

        let epsilon = 1e-6;
        assert_eq!(y_shape, &[1, 10, 2048], "Mismatch in y_shape");
        assert!((y_first - 0.014370).abs() < epsilon, "Mismatch in y_first");
        assert!((y_min + 0.284441).abs() < epsilon, "Mismatch in y_min");
        assert!((y_max - 0.188395).abs() < epsilon, "Mismatch in y_max");
        assert!((y_mean + 0.002183).abs() < epsilon, "Mismatch in y_mean");
        Ok(())
    }
}
