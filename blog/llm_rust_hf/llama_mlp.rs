use crate::config;
use crate::util;
use candle_core::{Module, Result, Tensor};
use candle_nn::Linear;
use safetensors::tensor::{SafeTensors, TensorView};

pub struct LlamaMLP {
    gate_proj: Linear,
    up_proj: Linear,
    down_proj: Linear,
}

// Inspired by https://github.com/huggingface/transformers/blob/v4.45.0/src/transformers/models/llama/modeling_llama.py#L282
impl LlamaMLP {
    pub fn new(
        gate_proj_weight: &TensorView,
        up_proj_weight: &TensorView,
        down_proj_weight: &TensorView,
    ) -> Result<Self> {
        let gate_proj = Linear::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&gate_proj_weight.data()),
                gate_proj_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            None,
        );
        let up_proj = Linear::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&up_proj_weight.data()),
                up_proj_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            None,
        );
        let down_proj = Linear::new(
            Tensor::from_slice(
                &util::convert_bytes_to_bf16(&down_proj_weight.data()),
                down_proj_weight.shape(),
                &config::DEVICE,
            )?
            .to_dtype(config::FORWARD_DTYPE)?,
            None,
        );
        Ok(Self {
            gate_proj,
            up_proj,
            down_proj,
        })
    }

    pub fn forward(&self, x: &Tensor) -> Result<Tensor> {
        let y = self
            .down_proj
            .forward(&(self.gate_proj.forward(x)?.silu()? * self.up_proj.forward(x)?)?)?;
        Ok(y)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_llama_mlp() -> Result<()> {
        let file_path = "../Llama-3.2-1B-Instruct/model.safetensors";
        let file_data = std::fs::read(file_path)?;
        let safetensors = SafeTensors::deserialize(&file_data)?;
        let llama_mlp = LlamaMLP::new(
            &safetensors.tensor("model.layers.0.mlp.gate_proj.weight")?,
            &safetensors.tensor("model.layers.0.mlp.up_proj.weight")?,
            &safetensors.tensor("model.layers.0.mlp.down_proj.weight")?,
        )?;

        let shape = (1, 10, config::HIDDEN_SIZE);
        let x = Tensor::full(0.5, shape, &config::DEVICE)?.to_dtype(config::FORWARD_DTYPE)?;
        let y = llama_mlp.forward(&x)?.to_dtype(candle_core::DType::F32)?;

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
        assert!((y_first + 0.053928).abs() < epsilon, "Mismatch in y_first");
        assert_eq!(y_shape, &[1, 10, 2048], "Mismatch in y_shape");
        assert!((y_min + 0.509184).abs() < epsilon, "Mismatch in y_min");
        assert!((y_max - 0.773810).abs() < epsilon, "Mismatch in y_max");
        assert!((y_mean - 0.010796).abs() < epsilon, "Mismatch in y_mean");
        Ok(())
    }
}
