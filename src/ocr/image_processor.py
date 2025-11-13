"""
Processador de imagens com OCR
"""
import io
from typing import Optional
from pathlib import Path
from PIL import Image
from loguru import logger

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract não instalado")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("easyocr não instalado")

from src.backend.config import settings


class ImageProcessor:
    """Processador de imagens para extração de texto via OCR"""
    
    def __init__(self):
        self.tesseract_path = settings.tesseract_path
        self.language = settings.ocr_language
        self.easyocr_reader = None
        
        if TESSERACT_AVAILABLE and self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
    
    def _init_easyocr(self):
        """Inicializa EasyOCR (lazy loading)"""
        if EASYOCR_AVAILABLE and not self.easyocr_reader:
            logger.info("Inicializando EasyOCR...")
            self.easyocr_reader = easyocr.Reader(['pt', 'en'])
        return self.easyocr_reader
    
    def extract_text(
        self, 
        image_bytes: bytes, 
        method: str = "tesseract"
    ) -> str:
        """
        Extrai texto de uma imagem usando OCR
        
        Args:
            image_bytes: Bytes da imagem
            method: Método OCR ('tesseract' ou 'easyocr')
            
        Returns:
            Texto extraído da imagem
        """
        try:
            # Carrega a imagem
            image = Image.open(io.BytesIO(image_bytes))
            
            # Pré-processamento da imagem
            image = self._preprocess_image(image)
            
            # Extrai texto baseado no método
            if method == "tesseract" and TESSERACT_AVAILABLE:
                text = self._extract_with_tesseract(image)
            elif method == "easyocr" and EASYOCR_AVAILABLE:
                text = self._extract_with_easyocr(image)
            else:
                logger.warning(f"Método {method} não disponível, usando fallback")
                text = self._extract_fallback(image)
            
            logger.success(f"Texto extraído com sucesso ({len(text)} caracteres)")
            return text
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            raise
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Pré-processa a imagem para melhorar a qualidade do OCR
        
        Args:
            image: Imagem PIL
            
        Returns:
            Imagem processada
        """
        # Converte para escala de cinza
        if image.mode != 'L':
            image = image.convert('L')
        
        # Aumenta o contraste (opcional)
        # from PIL import ImageEnhance
        # enhancer = ImageEnhance.Contrast(image)
        # image = enhancer.enhance(2.0)
        
        return image
    
    def _extract_with_tesseract(self, image: Image.Image) -> str:
        """Extrai texto usando Tesseract"""
        try:
            # Configurações do Tesseract
            config = '--psm 6 --oem 3'  # PSM 6: assume uniform block of text
            
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=config
            )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erro no Tesseract: {e}")
            raise
    
    def _extract_with_easyocr(self, image: Image.Image) -> str:
        """Extrai texto usando EasyOCR"""
        try:
            reader = self._init_easyocr()
            if not reader:
                raise Exception("EasyOCR não disponível")
            
            # Converte PIL Image para array numpy
            import numpy as np
            image_array = np.array(image)
            
            # Extrai texto
            results = reader.readtext(image_array)
            
            # Concatena todos os textos detectados
            text = ' '.join([result[1] for result in results])
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Erro no EasyOCR: {e}")
            raise
    
    def _extract_fallback(self, image: Image.Image) -> str:
        """Método fallback quando nenhum OCR está disponível"""
        logger.warning("Nenhum método OCR disponível")
        return "OCR não configurado. Instale pytesseract ou easyocr."
    
    def save_processed_image(
        self, 
        image: Image.Image, 
        output_path: Path
    ) -> None:
        """
        Salva imagem processada
        
        Args:
            image: Imagem PIL
            output_path: Caminho de saída
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            logger.info(f"Imagem salva em: {output_path}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar imagem: {e}")
            raise

