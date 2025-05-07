# ComfyUI-Indonesia-TTS

Repositori ini menyediakan integrasi model Text-to-Speech (TTS) Bahasa Indonesia dari Facebook (MMS-TTS-IND) ke dalam **ComfyUI**, sehingga Anda dapat langsung menyintesis suara berbahasa Indonesia dengan kontrol penuh via antarmuka node-based.

## 🔍 Ringkasan

- Menggunakan model **facebook/mms-tts-ind** dari Hugging Face
- Telah berhasil **menggunakan** `safetensors` agar bisa berjalan di ComfyUI  
- Menyediakan node khusus dengan parameter: teks, kecepatan, pitch, reverb, delay, dan kualitas audio
- Langsung drag-and-drop ke folder `custom_nodes` ComfyUI 

## 🚀 Fitur Utama

- **Support Bahasa Indonesia** via model MMS-TTS-IND : https://huggingface.co/facebook/mms-tts-ind
- **Kontrol Speed** (0.5×–2.0×)  
- **Pitch Shift** (±12 semitone)  
- **Quality**: low / medium / high  
- **Efek Audio**: reverb & delay sederhana  
- Integrasi mulus ke dalam workflow **ComfyUI** : Workflow tinggal pindahkan, cuma 1 node

## 📦 Instalasi

1. Clone repositori ini ke dalam direktori `custom_nodes` ComfyUI:
   ```bash
   git clone https://github.com/Anonymzx/Indonesia-TTS-ComfyUI.git
   ```

2. Ekstrak lalu taruh file modelnya disini  
   ```bash
   ~\ComfyUI\models\here
   ```
   **Download Model Disini**
   https://github.com/Anonymzx/ComfyUI-Indonesia-TTS/releases/tag/Indonesia-TTS
   
   ![Screenshot 2025-05-07 205608](https://github.com/user-attachments/assets/3bfcc2ea-6c2e-489d-8433-1fa59ce7f3e7)

   **I'm a beginner, so forgive me!**
   *terima kasih!*
   <br>
   **Special Thanks to Sanchit Gandhi for models**🙏
   <br>
   @Anonymzx
