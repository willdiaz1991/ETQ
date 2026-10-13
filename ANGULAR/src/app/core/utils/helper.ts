import * as CryptoJS from 'crypto-js';
import { Constants } from './constants';

export class Helper {
  /**
   * Encripta un texto usando AES
   * @param text Texto a encriptar
   * @returns Texto encriptado
   */
  static encrypt(text: string): string {
    const key = Constants.cryptoHelper;
    if (!key) {
      throw new Error('Crypto key not configured');
    }

    return CryptoJS.AES.encrypt(text, key).toString();
  }

  /**
   * Desencripta un texto encriptado con AES
   * @param encryptedText Texto encriptado
   * @returns Texto desencriptado
   */
  static decrypt(encryptedText: string): string {
    const key = Constants.cryptoHelper;
    if (!key) {
      throw new Error('Crypto key not configured');
    }

    const bytes = CryptoJS.AES.decrypt(encryptedText, key);
    return bytes.toString(CryptoJS.enc.Utf8);
  }

  /**
   * Convierte un archivo a Base64
   * @param file Archivo a convertir
   * @returns Promise con el string Base64
   */
  static convertFileBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
  }
}
