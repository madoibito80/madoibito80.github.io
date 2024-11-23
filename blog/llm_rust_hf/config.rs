// Sourced from https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct/blob/c4219cc9e642e492fd0219283fa3c674804bb8ed/config.json
pub const DEVICE: candle_core::Device = candle_core::Device::Cpu;
pub const HEAD_DIM: usize = 64;
pub const HIDDEN_SIZE: usize = 2048;
pub const MAX_POSITION_EMBEDDINGS: usize = 131072;
pub const NUM_ATTENTION_HEADS: usize = 32;
pub const NUM_HIDDEN_LAYERS: usize = 16;
pub const NUM_KEY_VALUE_HEADS: usize = 8;
pub const RMS_NORM_EPS: f64 = 1e-5;
pub mod rope_scaling {
    pub const FACTOR: f32 = 32.0;
    pub const HIGH_FREQ_FACTOR: f32 = 4.0;
    pub const LOW_FREQ_FACTOR: f32 = 1.0;
    pub const ORIGINAL_MAX_POSITION_EMBEDDINGS: usize = 8192;
}
pub const ROPE_THETA: f32 = 500000.0;
pub const BOS_TOKEN_ID: u32 = 128000;
pub const FORWARD_DTYPE: candle_core::DType = candle_core::DType::F32;
