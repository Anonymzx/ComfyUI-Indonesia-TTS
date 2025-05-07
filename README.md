# ComfyUI-Indonesia-TTS

Repositori ini menyediakan integrasi model Text-to-Speech (TTS) Bahasa Indonesia dari Facebook (MMS-TTS-IND) ke dalam **ComfyUI**, sehingga Anda dapat langsung menyintesis suara berbahasa Indonesia dengan kontrol penuh via antarmuka node-based.

## 🔍 Ringkasan

- Menggunakan model **facebook/mms-tts-ind** dari Hugging Face :contentReference[oaicite:0]{index=0}  
- Telah berhasil **mengonversi** `safetensors` agar bisa berjalan di ComfyUI  
- Menyediakan node khusus dengan parameter: teks, model variant, kecepatan, pitch, reverb, delay, dan kualitas audio
- Langsung drag-and-drop ke folder `custom_nodes` ComfyUI :contentReference[oaicite:1]{index=1}

## 🚀 Fitur Utama

- **Support Bahasa Indonesia** via model MMS-TTS-IND :contentReference[oaicite:2]{index=2}  
- **Kontrol Speed** (0.5×–2.0×)  
- **Pitch Shift** (±12 semitone)  
- **Quality**: low / medium / high  
- **Efek Audio**: reverb & delay sederhana  
- Integrasi mulus ke dalam workflow **ComfyUI** :contentReference[oaicite:3]{index=3}  

## 📦 Instalasi

1. Clone repositori ini ke dalam direktori `custom_nodes` ComfyUI:
   ```bash
   git clone https://github.com/<username>/Indonesia-TTS-ComfyUI.git \
     ~/ComfyUI/custom_nodes/Indonesia-TTS-ComfyUI
