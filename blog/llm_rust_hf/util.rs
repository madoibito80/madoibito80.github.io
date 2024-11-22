use half::bf16;

pub fn convert_bytes_to_bf16(data: &[u8]) -> &[half::bf16] {
    let bf16_data =
        unsafe { std::slice::from_raw_parts(data.as_ptr() as *const bf16, data.len() / 2) };
    bf16_data
}
