from transformers import pipeline
import torch
from typing import Optional
import config


class TranslationModel:
    def __init__(self):
        self.model = None
        self.is_loaded = False
        
    def load_model(self):
        """Load the NLLB translation model."""
        try:
            device = 0 if torch.cuda.is_available() else -1
            self.model = pipeline(
                "translation",
                model=config.MODEL_NAME,
                device=device,
                max_length=512
            )
            self.is_loaded = True
            print(f"Model {config.MODEL_NAME} loaded successfully on device: {'GPU' if device == 0 else 'CPU'}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.is_loaded = False
            raise
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Translate text from source language to target language."""
        if not self.is_loaded or not self.model:
            raise ValueError("Model not loaded")
        
        # Convert language codes to NLLB format
        src_lang_code = config.LANGUAGE_CODES.get(source_lang)
        tgt_lang_code = config.LANGUAGE_CODES.get(target_lang)
        
        if not src_lang_code or not tgt_lang_code:
            raise ValueError(f"Unsupported language pair: {source_lang} -> {target_lang}")
        
        try:
            # NLLB models expect src_lang and tgt_lang parameters
            result = self.model(
                text,
                src_lang=src_lang_code,
                tgt_lang=tgt_lang_code
            )
            return result[0]['translation_text']
        except Exception as e:
            print(f"Translation error: {e}")
            raise
    
    def translate_batch(self, texts: list[str], source_lang: str, target_lang: str) -> list[str]:
        """Translate multiple texts in a single batch for better performance."""
        if not self.is_loaded or not self.model:
            raise ValueError("Model not loaded")
        
        # Convert language codes to NLLB format
        src_lang_code = config.LANGUAGE_CODES.get(source_lang)
        tgt_lang_code = config.LANGUAGE_CODES.get(target_lang)
        
        if not src_lang_code or not tgt_lang_code:
            raise ValueError(f"Unsupported language pair: {source_lang} -> {target_lang}")
        
        try:
            # Process batch - model handles batching internally
            results = self.model(
                texts,
                src_lang=src_lang_code,
                tgt_lang=tgt_lang_code,
                batch_size=len(texts),
                clean_up_tokenization_spaces=True
            )
            return [r['translation_text'] for r in results]
        except Exception as e:
            print(f"Batch translation error: {e}")
            raise


# Global model instance
translation_model = TranslationModel()